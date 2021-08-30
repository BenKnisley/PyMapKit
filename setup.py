#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Created: 17 March, 2020
"""
from setuptools import setup

## Extract version from package __init__.py
from pymapkit import __version__ as version

## Get long description from readme file
with open('README.md') as f:
    long_desc_txt = f.read()

setup(
    name = "pymapkit",
    license = "MIT",
    version = version,
    author = "Ben Knisley",
    author_email = "benknisley@gmail.com",
    
    description = ("A Python based open-source mapping toolkit"),
    long_description=long_desc_txt,
    long_description_content_type='text/markdown',
    url = "https://github.com/BenKnisley/PyMapKit",
    
    install_requires=['pyproj==3.0.0.post1', 'numpy==1.19.1',],
    packages=["pymapkit"],

    keywords = "GIS Geography GeoSpatial MapTiles PyMapKit pymapkit",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Scientific/Engineering :: GIS",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
    ],
)


