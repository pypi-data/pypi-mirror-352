#!/usr/bin/env python
#kalakan

import os
from setuptools import setup, find_packages


def read(fname):
    """Read a file and return its contents."""
    with open(os.path.join(os.path.dirname(__file__), fname), "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    setup(
        name="kalakan-tts",
        version="1.0.0",
        description="A Text-to-Speech system for the Twi language",
        long_description=read("README.md"),
        long_description_content_type="text/markdown",
        author="Kalakan Team",
        author_email="info@kalakan.ai",
        url="https://github.com/kalakan-ai/kalakan-tts",
        packages=find_packages(),
        include_package_data=True,
        install_requires=[
            "torch>=1.10.0",
            "torchaudio>=0.10.0",
            "numpy>=1.20.0",
            "scipy>=1.7.0",
            "librosa>=0.8.0",
            "soundfile>=0.10.0",
            "matplotlib>=3.4.0",
            "pyyaml>=5.4.0",
            "tqdm>=4.60.0",
        ],
        extras_require={
            "api": [
                "fastapi>=0.68.0",
                "uvicorn>=0.15.0",
                "grpcio>=1.40.0",
                "grpcio-tools>=1.40.0",
                "protobuf>=3.17.0",
                "requests>=2.26.0",
            ],
            "training": [
                "tensorboard>=2.6.0",
                "wandb>=0.12.0",
                "pytorch-lightning>=1.4.0",
                "hydra-core>=1.1.0",
            ],
            "dev": [
                "pytest>=6.2.0",
                "pytest-cov>=2.12.0",
                "black>=21.8b0",
                "isort>=5.9.0",
                "flake8>=3.9.0",
                "mypy>=0.910",
            ],
        },
        entry_points={
            "console_scripts": [
                "kalakan=kalakan.cli:main",
                "kalakan-demo=kalakan.cli.demo:main",
                "kalakan-api=kalakan.cli.api:main",
                "kalakan-train=kalakan.cli:train",
                "kalakan-synthesize=kalakan.cli:synthesize",
            ],
        },
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: Apache Software License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Topic :: Multimedia :: Sound/Audio :: Speech",
            "Topic :: Scientific/Engineering :: Artificial Intelligence",
        ],
        python_requires=">=3.8",
    )