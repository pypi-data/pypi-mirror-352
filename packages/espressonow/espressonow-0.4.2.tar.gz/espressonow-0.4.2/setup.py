from setuptools import setup, find_packages
import click
import rich
import requests
import geocoder
import pydantic
import yaypp
from dotenv import load_dotenv
import typer

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="espressonow",
    version="0.4.2",
    author="Ethan Carter",
    author_email="ethanqcarter@gmail.com",
    description="A CLI tool for finding specialty coffee shops near you",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ethanqcarter/EspressoNow",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "espresso=espressonow.cli:main",
            "espressonow=espressonow.cli:main",
        ],
    },
    keywords="coffee, cli, maps, places, google-places, specialty-coffee",
    project_urls={
        "Bug Reports": "https://github.com/ethanqcarter/EspressoNow/issues",
        "Source": "https://github.com/ethanqcarter/EspressoNow",
    },
) 