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
__copyright__ = "Copyright 2020, Ben Knisley"
__license__ = "MIT"
__version__ = "0.1.4"
__status__ = "Planning"

## import all modules under PyMapKit
from . import vector_layer as vector_layer
from . import raster_layer as raster_layer
from . import tile_layer as tile_layer
from . import text_layer as text_layer
from . import label_layer as label_layer

## Import Map class
from .map import Map

## Import layer classes
from .vector_layer import VectorLayer
from .raster_layer import RasterLayer
from .tile_layer import TileLayer
from .text_layer import TextLayer
from .label_layer import LabelLayer


