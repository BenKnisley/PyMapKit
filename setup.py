#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date: 17 March, 2020
"""
from setuptools import setup

setup(
    name = "MapEngine",
    version = "0.0.0",
    author = "Ben Knisley",
    author_email = "benknisley@gmail.com",
    description = ("A module for rendering maps."),
    url = "https://github.com/BenKnisley/MapEngine",
    license = "MIT",
    keywords = "GIS map MapEngine",
    install_requires=['numpy','pyproj'],
    packages=["MapEngine",],
    package_dir={'MapEngine':'src'},
    long_description="...",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Scientific/Engineering :: GIS",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
    ],
)


