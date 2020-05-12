PyMapKit
==
#

## Intro
PyMapKit is a MIT-licensed Python toolkit for rendering maps and 
geospatial data. Designed to be simple to use and very extendable.

## Usage

Basic usage is very easy:

```python
## Import MapEngine Modules
from PyMapKit import MapEngine, CairoPainter, layer_from_file

## Create MapEngine object
m = MapEngine.MapEngine()

## Set Map Attributes
m.set_location(40.0, -81.0)
m.set_scale(500)
m.set_size(500, 500)

## Create data layers
lay1 = MapEngine.layer_from_file(path1)
lay2 = MapEngine.layer_from_file(path2)
lay3 = MapEngine.layer_from_file(path3)

## Add layers to Map Object
m.add_layer(lay1)
m.add_layer(lay2)
m.add_layer(lay3)


sf = cairo.ImageSurface(cairo.Format.RGB24, m.width, m.height)
cr = cairo.Context(surface)

## Render onto canvas
map_obj.render(cr)

## Save output file
sf.save_png(out_path)
```

## Installation
