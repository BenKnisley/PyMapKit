"""
Project: PyMapKit
File: map.py
Title: Map Class Definition
Function: Define the Map class that pymapkit project is build around.
Author: Ben Knisley [benknisley@gmail.com]
Created: 5 January, 2021
"""
import pyproj
import numpy as np

class Map:
    def __init__(self):
        ''' '''
        ## Create a list to hold layers
        self.layers = [] #! Add type hint

        ## Hold a renderer
        self.renderer = None

        ## Create integers to hold width and height
        self.width: int = 0
        self.height: int = 0

        ## Create a crs for input geographic points, & output projected points
        ## Default to WGS84 & Mercator
        self.geographic_crs: pyproj.crs.CRS = pyproj.crs.CRS("EPSG:4326")
        self.projected_crs: pyproj.crs.CRS = pyproj.crs.CRS("EPSG:3785")

        ## Create transformer objects
        self.transform_geo2proj = pyproj.Transformer.from_crs(self.geographic_crs, self.projected_crs)
        self.transform_proj2geo = pyproj.Transformer.from_crs(self.projected_crs, self.geographic_crs)

        ## Create a variable to hold scale
        self._proj_scale = 1.0 ## unit/pixel
        
        ## Set projection location
        self.proj_x = 0
        self.proj_y = 0

    ##
    ## Layer methods
    ##

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
        new_layer._activate(self)

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
        del_layer._deactivate()
        self.layers.remove(del_layer)
    
    ##
    ## Location Methods
    ##
    
    def set_location(self, latitude, longitude):
        ''' '''
        geo_y, geo_x = latitude, longitude
        proj_x, proj_y = self.geo2proj(geo_x, geo_y)
        self.set_projection_coordinates(proj_x, proj_y)

    def get_location(self):
        ''' '''
        geo_x, geo_y = self.proj2geo(self.proj_x, self.proj_y)
        latitude, longitude = geo_y, geo_x ## I do this for now
        return latitude, longitude

    def set_projection_coordinates(self, new_x, new_y):
        ''' '''
        self.proj_x = new_x
        self.proj_y = new_y
    
    def get_projection_coordinates(self):
        ''' '''
        return self.proj_x, self.proj_y

    ##
    ## Reference System Methods
    ##
    
    def set_geographic_crs(self, new_crs):
        '''  '''
        if isinstance(new_crs, str):
            self.geographic_crs = pyproj.crs.CRS(new_crs)

        elif isinstance(new_crs, pyproj.crs.CRS):
            self.geographic_crs = pyproj.crs.CRS(new_crs)
        
        else:
            pass #@ NOTE: throw errors
     
    def set_projection(self, new_crs): #@ Rename to set_crs
        ''' '''
        if isinstance(new_crs, str):
            self.projected_crs = pyproj.crs.CRS(new_crs)

        elif isinstance(new_crs, pyproj.crs.CRS):
            self.projected_crs = pyproj.crs.CRS(new_crs)
        
        else:
            pass #@ NOTE: throw errors
     

    ##
    ## Scale Methods
    ##
    
    def set_scale(self, new_scale):
        '''
        '''
        ## Get unit code of base unit of projection
        proj_unit = self.projected_crs.axis_info[0].unit_code

        if proj_unit == 9003: ## 9003 == US survey foot
            ## Meters to feet
            new_scale = new_scale * 3.28084

        if proj_unit == 9122: ## 9122 == degree':
            ## degrees to meters
            new_scale = new_scale / 110570

        #@ NOTE: Add more units

        ## Set scale in proj units per pix
        self._proj_scale = float(new_scale)

    def get_scale(self):
        """
        """
        ## Get current scale in units/pix
        proj_scale = self._proj_scale

        ## Get unit code of base unit of projection
        proj_unit = self.projected_crs.axis_info[0].unit_code

        if proj_unit == 9003: ## 9003 == US survey foot
            ## Meters to feet
            return proj_scale / 3.28084

        if proj_unit == 9122: ## 9122 == degree':
            ## meters to degrees
            return proj_scale * 110570

    ##
    ## Canvas Size Methods
    ##

    def set_size(self, width, height):
        """
        Sets the size in pixels of the canvas

        Arguments:
            - width: int - the new width of the map canvas
            - height: int - the new width of the map canvas

        Optional Arguments:
            None

        Returns: None
        """
        self.width = width
        self.height = height
    
    def get_size(self):
        """ """
        return self.width, self.height

    ##
    ## Backend, background, and rendering methods
    ##

    def set_backend(self, backend):
        '''
        '''
        self.renderer = backend
        pass
    
    def render(self, output=None, *args):
        ''' '''

        output_file = None
        
        if self.renderer.is_canvas(output):
            canvas = output
        else:
           canvas = self.renderer.new_canvas(self.width, self.height)
           output_file = output
        
        '''
        if self._background_color:
            ## Draw background
            self.renderer.draw_background(canvas, self._background_color)
        '''

        ## Draw each layer, pass renderer, and canvas to each object
        for layer in self.layers:
            layer.draw(self.renderer, canvas)
        
        ## Save or display canvas
        self.renderer.save(canvas, output_file)

    
    
    ##
    ## Conversion methods
    ##
    
    def geo2proj(self, geo_x, geo_y):
        ''' '''
        return self.transform_geo2proj.transform(geo_x, geo_y)
    
    def proj2geo(self, proj_x, proj_y):
        ''' '''
        return self.transform_geo2proj.transform(proj_x, proj_y)


    def proj2pix(self, proj_x, proj_y):
        ''' '''
        ## Flag true if input is list
        list_flag = False

        ## Convert list to numpy array
        if isinstance(proj_x, list):
            proj_x = np.array(proj_x)
            proj_y = np.array(proj_y)
            list_flag = True
        
        ## Do math logic on all points
        # NOTE: @ self._proj_scale has to be a float!
        pix_x = ((proj_x - self.proj_x) / self._proj_scale) + int(self.width / 2) #! NOTE: a round(...) might be better 
        pix_y = -((proj_y - self.proj_y) / self._proj_scale) + int(self.height / 2) #! NOTE: a round(...) might be better 

        ## Convert numpy array to list
        if list_flag:
            pix_x = list(pix_x)
            pix_y = list(pix_y)
        
        return pix_x, pix_y

    def pix2proj(self, pix_x, pix_y):
        ''' '''
        ## Flag true if input is list
        list_flag = False

        ## Convert list to numpy array
        if isinstance(pix_x, list):
            pix_x = np.array(pix_x)
            pix_y = np.array(pix_y)
            list_flag = True
        
        ## Do math logic on all points
        #! NOTE: @ self._proj_scale has to be a float!
        #! NOTE: a round(...) might be better 
        proj_x = self.proj_x + ((pix_x - int(self.width / 2)) * self._proj_scale) 
        proj_y = (self.proj_y + ((pix_y - int(self.height / 2)) * self._proj_scale) )

        ## Convert numpy array to list
        if list_flag:
            proj_x = list(proj_x)
            proj_y = list(proj_y)
        
        return proj_x, proj_y


    def geo2pix(self, geo_x, geo_y):
        ''' '''
        pass
    
    def pix2geo(self, pix_x, pix_y):
        ''' '''
        pass
