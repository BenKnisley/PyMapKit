#!/usr/bin/env python3
"""
MapEngine - A module for rendering maps
"""
from __future__ import absolute_import

## Import MapEngine
from .MapEngine import MapEngine

## Import Vector Layer Functions
from .VectorLayer import from_shapefile as layer_from_shapefile

## Import Cario Functions
from .CairoPainter import draw_point
from .CairoPainter import draw_line
from .CairoPainter import draw_polygon


__author__ = "Ben Knisley (benknisley@gmail.com)"
__license__ = "MIT"
__version__ = "0.0.0"



