#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date: 17 March, 2020
"""
from setuptools import setup

setup(
    name = "PyMapKit",
    version = "0.1",
    author = "Ben Knisley",
    author_email = "benknisley@gmail.com",
    description = ("A packages for rendering maps."),
    url = "https://github.com/BenKnisley/PyMapKit",
    license = "MIT",
    keywords = "GIS map PyMapKit MapEngine",
    #requires_python='>=3.6',
    #requires_external='GDAL (>=1.8)',
    install_requires=['numpy','pyproj'],
    packages=["PyMapKit",],
    long_description="...",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Scientific/Engineering :: GIS",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
    ],
)


