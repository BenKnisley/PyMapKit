"""
Project: PyMapKit
File: map.py
Title: Map Class Definition
Function: Define the Map class that pymapkit project is build around.
Author: Ben Knisley [benknisley@gmail.com]
Created: 5 January, 2021
"""
import pyproj


class Map:
    def __init__(self):

        ## Create a list to hold layers
        self.layers = [] #! Add type hnt

        ## Create integers to hold width and height
        self.width: int = 0
        self.height: int = 0

        ## Create a crs for input geographic points, & output projected points
        ## Default to WGS84 & Mercator
        self.geographic_crs = pyproj.crs.CRS("EPSG:4326")
        self.projected_crs = pyproj.crs.CRS("EPSG:3785")

        ## Create transformer objects
        self.transform_geo2proj = pyproj.Transformer.from_crs(self.geographic_crs, self.projected_crs)
        self.transform_proj2geo = pyproj.Transformer.from_crs(self.projected_crs, self.geographic_crs)

        ## Set scale
        self.scale = 1

        ## Set projection location
        self.x_coordinate = 0
        self.y_coordinate = 0

