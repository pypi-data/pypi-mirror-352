from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="cloud189",
    version="0.1.1",
    author="s0urce",
    author_email="me@src.moe",
    description="A Python SDK for interacting with Cloud189",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/s0urcelab/cloud189",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
) 