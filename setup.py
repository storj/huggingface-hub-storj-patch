import setuptools

setuptools.setup(
    name="huggingface_hub_storj_patch",
    version="0.0.6",
    author="Kaloyan Raev",
    author_email="kaloyan@storj.io",
    description="Monkey patch for huggingface_hub to download Git-LFS blobs from Storj",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    keywords="model-hub machine-learning models natural-language-processing deep-learning pytorch pretrained-models storj patch linksharing decentralized cloud storage",
    license="Apache",
    url="https://github.com/storj/huggingface-hub-storj-patch",
    packages=setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.7.0',
    py_modules=["huggingface_hub_storj_patch"],
    package_dir={'':'huggingface_hub_storj_patch/src'},
    install_requires=[
        "huggingface-hub>=0.13"
    ]
)