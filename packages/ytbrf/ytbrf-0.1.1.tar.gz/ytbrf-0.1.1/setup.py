from setuptools import setup

setup(
    name="ytbrf",
    version="0.1.1",
    packages=["ytbrf"],
    install_requires=[
        "yt-dlp>=2023.12.30",
        "typer>=0.9.0",
        "rich>=13.7.0",
        "google-api-python-client>=2.108.0",
        "google-auth-oauthlib>=1.1.0",
        "transformers>=4.36.0",
        "torch>=2.1.0",
        "sentencepiece>=0.1.99",
        "protobuf>=4.25.1",
    ],
    entry_points={
        "console_scripts": [
            "ytbrf=ytbrf:main",
        ],
    },
    author="allenlsy",
    author_email="allenlsy@gmail.com",
    description="A CLI tool to transcribe, summarize and translate YouTube videos",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
) 