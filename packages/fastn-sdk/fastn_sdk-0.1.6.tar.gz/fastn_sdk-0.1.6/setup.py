# setup.py

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fastn-sdk",
    version="0.1.6",
    author="Fastn AI",
    author_email="info@fastn.ai",
    description="Official Python SDK for the Fastn Automation Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fastnai/fastn-python-sdk",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
) 