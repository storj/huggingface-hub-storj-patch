import mmap
import os
import requests
import huggingface_hub
from huggingface_hub.constants import _as_int, _is_true
from huggingface_hub.file_download import HfFileMetadata, HEADER_FILENAME_PATTERN, logger, _request_wrapper
from huggingface_hub.utils import hf_raise_for_status, logging, tqdm, validate_hf_hub_args
from typing import BinaryIO, Dict, Optional, Union
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor

HF_HUB_NO_STORJ: bool = _is_true(os.environ.get("HF_HUB_USE_STORJ"))

HF_HUB_STORJ_PARALLELISM: int = (
    _as_int(os.environ.get("HF_HUB_STORJ_PARALLELISM")) or 16
)

HF_HUB_STORJ_URL_PREFIX = os.environ.get(
    "HF_HUB_STORJ_URL_PREFIX",
    "https://link.storjshare.io/raw/juzlwaj7ovnst5gtkv2km3rkriha/lfs-huggingface"
)

original_hf_hub_url = huggingface_hub.file_download.hf_hub_url

def patched_hf_hub_url(
    repo_id: str,
    filename: str,
    *,
    subfolder: Optional[str] = None,
    repo_type: Optional[str] = None,
    revision: Optional[str] = None,
) -> str:
    url = original_hf_hub_url(repo_id=repo_id, filename=filename, subfolder=subfolder, repo_type=repo_type, revision=revision)

    print(f"hf_hub_url: {url}")

    return url

huggingface_hub.file_download.hf_hub_url = patched_hf_hub_url


original_get_hf_file_metadata = huggingface_hub.file_download.get_hf_file_metadata

@validate_hf_hub_args
def patched_get_hf_file_metadata(
    url: str,
    token: Union[bool, str, None] = None,
    proxies: Optional[Dict] = None,
    timeout: float = 10,
) -> HfFileMetadata:
    metadata = original_get_hf_file_metadata(url=url, token=token, proxies=proxies, timeout=timeout)

    location = metadata.location
    parsed_target = urlparse(metadata.location)
    if not HF_HUB_NO_STORJ and parsed_target.netloc == "cdn-lfs.huggingface.co":
        location = HF_HUB_STORJ_URL_PREFIX + parsed_target.path

    return HfFileMetadata(
        commit_hash=metadata.commit_hash,
        etag=metadata.etag,
        location=location,
        size=metadata.size,
    )

huggingface_hub.file_download.get_hf_file_metadata = patched_get_hf_file_metadata


def http_get_chunk(url: str, start: int, end: int, mm: mmap.mmap, progress: tqdm):
    headers = {'Range': f'bytes={start}-{end}'}
    response = requests.get(url, headers=headers, stream=True)
    for chunk in response.iter_content(chunk_size=10*1024*1024):
        mm[start:start+len(chunk)] = chunk
        start += len(chunk)
        progress.update(len(chunk))


original_http_get = huggingface_hub.file_download.http_get

def patched_http_get(
    url: str,
    temp_file: BinaryIO,
    *,
    proxies=None,
    resume_size=0,
    headers: Optional[Dict[str, str]] = None,
    timeout=10.0,
    max_retries=0,
):
    print(f"http_get url: {url}")
    
    if HF_HUB_NO_STORJ or HF_HUB_STORJ_PARALLELISM <= 1 or resume_size > 0 or urlparse(url).netloc != "link.storjshare.io":
        return original_http_get(url=url, temp_file=temp_file, proxies=proxies, resume_size=resume_size, headers=headers, timeout=timeout, max_retries=max_retries)

    r = _request_wrapper(
        method="HEAD",
        url=url,
        stream=True,
        proxies=proxies,
        headers=headers,
        timeout=timeout,
        max_retries=max_retries,
    )
    hf_raise_for_status(r)
    content_length = int(r.headers.get("Content-Length"))

    displayed_name = url
    content_disposition = r.headers.get("Content-Disposition")
    if content_disposition is not None:
        match = HEADER_FILENAME_PATTERN.search(content_disposition)
        if match is not None:
            # Means file is on CDN
            displayed_name = match.groupdict()["filename"]

    # Truncate filename if too long to display
    if len(displayed_name) > 22:
        displayed_name = f"(…){displayed_name[-20:]}"

    with tqdm(
        unit="B",
        unit_scale=True,
        total=content_length,
        initial=resume_size,
        desc=f"Downloading {displayed_name}",
        disable=bool(logger.getEffectiveLevel() == logging.NOTSET),
    ) as progress:
        os.posix_fallocate(temp_file.fileno(), 0, content_length)
        with mmap.mmap(temp_file.fileno(), 0) as mm:
            chunks = HF_HUB_STORJ_PARALLELISM
            chunk_size = content_length // chunks
            with ThreadPoolExecutor(max_workers=chunks) as executor:
                futures = []
                for i in range(chunks):
                    start = i * chunk_size
                    end = start + chunk_size - 1 if i != chunks - 1 else content_length - 1
                    futures.append(executor.submit(http_get_chunk, url, start, end, mm, progress))
                for future in futures:
                    future.result()  # raise exception if any

huggingface_hub.file_download.http_get = patched_http_get
