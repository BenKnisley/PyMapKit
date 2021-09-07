"""
Project: PyMapKit
Title: PyMapKit
Function: PyMapKit is a Python based open-source mapping toolkit.
Author: Ben Knisley [benknisley@gmail.com]
Created: 1 January, 2020
"""
## Define metadata
__author__ = "Ben Knisley"
__maintainer__ = "Ben Knisley"
__email__ = "benknisley@gmail.com"
__copyright__ = "Copyright 2021, Ben Knisley"
__license__ = "MIT"
__version__ = "0.1.6"
__status__ = "Pre-Alpha"

## Import Map class
from .map import Map

## Import Base Classes
from .base_renderer import BaseRenderer
from .skia_renderer import SkiaRenderer
from .base_style import BaseStyle, ParentStyle

## Import Layers
from .raster_layer import RasterLayer
from .vector_layer import VectorLayer
from .tile_layer import TileLayer

from .label_layer import StaticTextLayer
