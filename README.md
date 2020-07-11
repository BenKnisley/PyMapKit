PyMapKit
==

PyMapKit is a Python based open-source mapping toolkit.
It can be used for creating maps, visualizing geospatial data, and developing GIS applications.
It is built to be modular: so it can be very simple to use, but also to be integrated into complex mapping applications.

## Basic Usage
```python
## Import MapEngine Modules
import PyMapKit
from PyMapKit import CairoPainter as renderer

## Create MapEngine object
m = PyMapKit.MapEngine()

## Set Map Attributes
m.set_size(500, 500)
m.set_location(40.0, -81.0)
m.set_scale(500)

## Add tile layer
tile_layer = TileLayer("https://tileserver.com/tile/{z}/{y}/{x}")

## Create data layers
vect_layer = PyMapKit.VectorLayer("./path/to/file.shp")
rast_layer = PyMapKit.VectorLayer("./path/to/file.tiff")

## Add layers to Map Object
m.add_layer(tile_layer)
m.add_layer(vect_layer)
m.add_layer(rast_layer)

## Using PyCairo for rendering
sf = cairo.ImageSurface(cairo.Format.RGB24, m.width, m.height)
cr = cairo.Context(surface)

## Render onto canvas using CairoPainter as renderer
m.render(renderer, cr)

## Save output file
sf.save_png("./map.png")
```

## Installation
PyMapKit has only been used and tested on Ubuntu. Windows and OSX support will be implemented in the future.

#### Prerequisites

Linux/Ubuntu
```bash
sudo apt install python3-gdal python3-cairo
```

#### Install


```bash
pip install PyMapKit
```

## Data Types
As of right now PyMapKit has layers to support:
* Vector data
* Raster data
* Map Tiles
* Simple text labels

It will support:
* Geo referenced text labels


## Backends
At the moment: PyMapKit can only use PyCario as rendering backend. 
