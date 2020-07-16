Todo List
===
#

## General Project
* Create a Geo Referenced Label Feature
* Write docs for project
* Write Tests for project
* Add feature to add scale bar, compass rose, and other basic map elements
* Create a QT backend
* Create a PIL backend
* Figure out a clean way to select which backend to use
#


## MapEngine
* Rename MapEngine to Map
* Add docs & tests to set_backend
* Replace NumPy arrays with Python lists in geo2proj, proj2pix, etc methods
* [Maybe] Move geo2tile and scale2zoom from TileLayer to MapEngine
#


## VectorLayer
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


## RasterLayer
* Make loading raster more efficient
* Make removing nodata pixels more efficient
* Rename clear_nodata flag
#


## TileLayer
* Add projection support, and remove projection warning
* Add preload next zoom levels
#


## TextLayer
* Maybe add image support
#


## CairoBackend
* Remove use of color_converter method inside drawing methods to improve render time
* Rename refactor variables 
#

## TkBackend
* Rename refactor variables 
#

