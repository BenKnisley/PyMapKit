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

        ## Create variables to hold scale
        self._scale = 1 ## m/pix
        self._proj_scale = 1 ## unit/pixel
        
        ## Set projection location
        self.x_coordinate = 0
        self.y_coordinate = 0


    ######################
    ## Layer methods
    ######################

    def add(self, new_layer, index=-1):
        """
        Adds a new layer to the map.
        By default the new layer is added to the end of the layer list, and thus on top of existing map layers.

        Arguments:
            - new_layer - a pymapkit.MapLayer object to be added to the Map objects layer list

            Optional:__
                - index=-1: the index where to insert the new layer. -1 adds layer to the top of the map, 0 to the bottom.

        Returns: None
        """
        ## Call activate on new_layer
        new_layer.activate(self)

        ## Add layer. 
        if index == -1:
            self.layers.append(new_layer)
        else:
            self.layers.insert(index, new_layer)
        
    def remove(self, del_layer):
        """ 
        Removes a layer from the map.

        Arguments
            - del_layer - the layer to remove from the layer list. del_layer must exist in map.layers.

            Optional:
                - None

        Returns: None
        """
        ## Call deactivate on del_layer
        del_layer.deactivate()

        ## 
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
    
    def set_scale(self, new_scale):
        ''' '''
        ## NOTE: PyProj gives us a way to convert
        #projected_crs.axis_info[0].unit_conversion_factor
        pass


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
