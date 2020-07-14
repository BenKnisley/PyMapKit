Todo List
===
#

## General Project
#### - Create a Geo Referenced Label Feature

#### - Add feature to add scale bar, compass rose, and other basic map elements

#### - Create a QT or TK rendering backend

#### - Figure out a clean way to select which backend to use
#


## MapEngine
#### - Replace NumPy arrays with Python lists in geo2proj, proj2pix, etc methods
#### - [Maybe] Move geo2tile and scale2zoom from TileLayer to MapEngine
#


## VectorLayer
#### - Replace NumPy arrays with Python lists where efficient
#### - Try out storing features in a R-tree for fast spatial indexing
#### - Cleanup _project_features method
#### - Cleanup data import functions
#### - Add a SpatiaLite query import function 
#### - Add a PostGIS query import function 
#


## RasterLayer
#### - Make loading raster more efficient
#### - Make removing nodata pixels more efficient
#### - Rename clear_nodata flag
#


## TileLayer
#


## TextLayer
#### - Maybe add image support
#