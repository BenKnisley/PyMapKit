Todo List
===
#


## General Project
---
* Write docs for project
* Write Tests for project
#

### Map Class
* Add docs & tests to set_backend
* Replace NumPy arrays with Python lists in geo2proj, proj2pix, etc methods
* [Maybe] Move geo2tile and scale2zoom from TileLayer to Map object
#


## Data Layers
---
* Create a Geo Referenced Label Feature
* Add layer to add scale bar, compass rose, and other basic map elements
#

### VectorLayer Class
* Replace NumPy arrays with Python lists where efficient
* Cleanup _project_features method
* Cleanup data import functions
* Add a SpatiaLite query import function 
* Add a PostGIS query import function 
* Add Line Dash feature
* Remove pre _ from should be public vars
* Add icons for points features
* Add a VectorLayer.run method that takes a function to style features.
* Try out storing features in a R-tree for fast spatial indexing
#

### RasterLayer Class
* Make loading raster more efficient
* Make removing nodata pixels more efficient
* Rename clear_nodata flag
#

### TileLayer Class
* Add projection support, and remove projection warning
* Add preload next zoom levels
#

### TextLayer Class
* Maybe add image support
#


## Backend Renderers
---
* Create a PIL backend
* Create a QT backend

### CairoBackend
* Remove use of color_converter method inside drawing methods to improve render time
* Rename refactor variables 
#

### TkBackend
* Rename refactor variables 
#

