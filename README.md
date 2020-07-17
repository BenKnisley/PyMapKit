PyMapKit
==

PyMapKit is a Python based open-source mapping toolkit.
It can be used for creating maps, visualizing geospatial data, and developing GIS applications.
It is built to be modular: so it can be very simple to use, but also to be integrated into complex mapping applications.

## Basic Usage
```python
## Import PyMapKit
import PyMapKit

## Create a PyMapKit Map object
m = PyMapKit.Map()

## Set Map Attributes
m.set_size(500, 500)
m.set_location(40.0, -81.0)
m.set_scale(500)

## Add tile layer
tile_layer = PyMapKit.TileLayer("https://tileserver.com/tile/{z}/{y}/{x}")

## Create data layers
vect_layer = PyMapKit.VectorLayer("./path/to/file.shp")
rast_layer = PyMapKit.VectorLayer("./path/to/file.tiff")

## Add layers to Map Object
m.add_layer(tile_layer)
m.add_layer(vect_layer)
m.add_layer(rast_layer)

## Render to file
m.render("map.png")

```

## Installation

### External Dependencies
PyMapKit requires two external libraries that require a non Python component installed. You will need to install these on your system before installing PyMapKit. These dependencies are:

* [GDAL/OGR](https://gdal.org/): for loading geospatial data, and warping raster datasets
* [Cario](https://www.cairographics.org/pycairo/): For drawing operations

#### Linux/Ubuntu:
```bash
sudo apt install python3-gdal python3-cairo
```

#### Windows:
```bash
Coming soon
```

#### Mac OSx:
```bash
Coming soon
```

### Installing PyMapKit
To install PyMapKit from PyPI simply run: 
```bash
pip install PyMapKit
```

Or to install from the GitHub repo:
```bash
git clone https://github.com/BenKnisley/PyMapKit.git
pip install -r ./PyMapKit/requirements.txt
pip install ./PyMapKit
```

#### Developer Extras
If you are contributing to PyMapKit make sure you also install the dev requirements as well.
```bash
pip install -r requirements_dev.txt
```
