# Monkey patch for HuggingFace Hub to download Git-LFS blobs from Storj

This patch aims to demonstrate the transfer speed that can be achieved with `huggingface_hub` Python library when utilizing the power of the [Storj Decentralized Cloud Storage](https://storj.io).

HuggingFace Hub stores all large files in Git-LFS.

![image](https://github.com/storj/huggingface-hub-storj-patch/assets/468091/b3c8d6d6-14fd-43c2-9396-91d4d3eba62f)

When the `huggingface_hub` Python library requests to download such a file, the download request is redirected to the Git-LFS CDN hosted at `cdn-lfs.huggingface.co`.

This monkey patch modifies the `huggingface_hub` library to redirect Git-LFS downloads to the Storj Linksharing service hosted at `link.storjshare.io`.

## Prerequisites

The Git-LFS blobs for the respective AI model must be replicated to a Storj bucket and shared it with the [Storj Linksharing Service](https://docs.storj.io/dcs/api-reference/linksharing-service).

We have already replicated the Git-FLS blobs of the [StarCoder](https://huggingface.co/bigcode/starcoder) model to a Storj bucket and shared it: https://link.storjshare.io/raw/juzlwaj7ovnst5gtkv2km3rkriha/lfs-huggingface

If you want to use another AI model, you need to use your own Storj bucket and then configure the patch to use it. See [Configuration](#hf_hub_storj_url_prefix) for more details.

## Installation

First, install the patch module:

```sh
pip install huggingface-hub-storj-patch
```

Then add the following import statement at the top, before any other import, of your Python script:

```python
import huggingface_hub_storj_patch
```

Now you can run your script. If the patch is applied successfully, you will see it printing the URLs from which the `huggingface_hub` library is downloading.

![image](https://github.com/storj/huggingface-hub-storj-patch/assets/468091/ad50968c-7959-4a6a-8f63-540eb70372ba)

## Configuration

These environment variables can configure the behavior of the patch.

### HF_HUB_NO_STORJ

If set to `true`, downloads won't be redirected to the Storj Linksharing Service as if the patch is not applied.

### HF_HUB_STORJ_PARALLELISM

Configures how many parallel download connections are open to the Storj Linksharing Service. The default value is `16`.

### HF_HUB_STORJ_URL_PREFIX

Configures the URL to the shared Storj bucket that replicates the Git-LFS blobs of the AI model. The default value is the bucket that replicates the StarCoder model: https://link.storjshare.io/raw/juzlwaj7ovnst5gtkv2km3rkriha/lfs-huggingface
