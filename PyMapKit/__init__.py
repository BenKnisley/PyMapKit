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


## Import Map class
from .Map import Map

## 
from . import VectorLayer as vector
from . import RasterLayer as raster
from . import TileLayer as tile
from . import TextLayer as text
from . import LabelLayer as label


## Import data layer classes
from .VectorLayer import VectorLayer
from .RasterLayer import RasterLayer
from .TileLayer import TileLayer
from .TextLayer import TextLayer
from .LabelLayer import LabelLayer


