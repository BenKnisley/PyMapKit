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

## Import data layer classes
from . import VectorLayer as vector #! Import all like this??
from .VectorLayer import VectorLayer

from . import RasterLayer as raster
from .RasterLayer import RasterLayer

from . import TileLayer as tile
from .TileLayer import TileLayer

from . import TextLayer as text
from .TextLayer import TextLayer

from . import LabelLayer as label
from .LabelLayer import LabelLayer




