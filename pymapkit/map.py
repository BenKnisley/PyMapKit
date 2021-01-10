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
        ''' '''
        ## Create a list to hold layers
        self.layers = [] #! Add type hint

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

    ######################
    ## Layer methods
    ######################

    def add(self, new_layer, index=0):
        ''' Add a layer to the map '''
        new_layer.activate(self)
        self.layers.insert(index, new_layer)
        


    def remove(self, del_layer):
        ''' Remove a layer from the map '''
        del_layer.deactivate()
        self.layers.remove(del_layer)
    
    ##
    ##
    ##
    
    def set_location(self, latitude, longitude):
        ''' '''
        pass

    def get_location(self):
        ''' '''
        pass
    
    def get_projection_coordinates(self):
        ''' '''
        pass
    
    def set_projection_coordinates(self, x, y):
        ''' '''
        pass
    
    ##
    ##
    ##
    
    def set_size(self, width, height):
        ''' '''
        pass
    
    def set_backend(self, backend):
        '''  '''
        pass
    
    def render(self, *args):
        ''' '''
        pass
    
    
    ##
    ##
    ##
    
    def set_geographic_crs(self, new_crs):
        '''  '''
        pass
    
    def set_projection(self, new_projection):
        ''' '''
        pass
    
    ##
    ##
    ##
    
    def geo2proj(self, geo_x, geo_y):
        ''' '''
        pass
    
    def proj2geo(self, proj_x, proj_y):
        ''' '''
        pass
    
    def proj2pix(self, proj_x, proj_y):
        ''' '''
        pass
    
    def pix2proj(self, pix_x, pix_y):
        ''' '''
        pass
    
    def geo2pix(self, geo_x, geo_y):
        ''' '''
        pass
    
    def pix2geo(self, pix_x, pix_y):
        ''' '''
        pass
