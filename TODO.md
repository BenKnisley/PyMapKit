Todo List
===
#

## General Project
* Write docs for project
* Write Tests for project
* Create a Geo Referenced Label Feature
* Add feature to add scale bar, compass rose, and other basic map elements
* Create a QT or TK rendering backend
* Figure out a clean way to select which backend to use
#


## MapEngine
* Rename MapEngine to Map
* Replace NumPy arrays with Python lists in geo2proj, proj2pix, etc methods
* [Maybe] Move geo2tile and scale2zoom from TileLayer to MapEngine
#


## VectorLayer
* Replace NumPy arrays with Python lists where efficient
* Try out storing features in a R-tree for fast spatial indexing
* Cleanup _project_features method
* Cleanup data import functions
* Add a SpatiaLite query import function 
* Add a PostGIS query import function 
* Add Line Dash feature
* Remove pre _ from should be public vars
* Add icons for points features
* Add a VectorLayer.run method that takes a function to style features.
#


## RasterLayer
* Make loading raster more efficient
* Make removing nodata pixels more efficient
* Rename clear_nodata flag
#


## TileLayer
* Add projection support
* Add preload next zoom levels
#


## TextLayer
* Maybe add image support
#


## CairoBackend
* Remove use of color_converter method inside drawing methods to improve render time
#