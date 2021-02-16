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


def get_renderer(renderer_name):
    """ 
    Returns a named renderer instance based on input string


    Args:
        renderer_name (str): The name of the renderer object to return.
    
    Returns:
        renderer (base_renderer): A renderer object of the type given with 
        renderer_name.
    """
    if renderer_name in ('skia', 'pyskia'):
        from .skia_renderer import SkiaRenderer
        #! NOTE: Don't forget to update the tests too
        return object()

class Map:
    def __init__(self, renderer='pyskia'):
        ''' '''
        ## Create a list to hold layers
        self.layers = [] #! Add type hint

        ## Hold a renderer
        self.renderer = None
        if isinstance(renderer, str):
            self.renderer = get_renderer(renderer)
        else: 
            self.renderer = renderer

        ## Create integers to hold width and height. Default 500x500
        self.width: int = 500
        self.height: int = 500

        ## Create a crs for input geographic points, & output projected points
        ## Default to WGS84 & Mercator
        self.geographic_crs: pyproj.crs.CRS = pyproj.crs.CRS("EPSG:4326")
        self.projected_crs: pyproj.crs.CRS = pyproj.crs.CRS("EPSG:3785")

        ## Create transformer objects
        self.transform_geo2proj = pyproj.Transformer.from_crs(self.geographic_crs, self.projected_crs, always_xy=True)
        self.transform_proj2geo = pyproj.Transformer.from_crs(self.projected_crs, self.geographic_crs, always_xy=True)

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

        Adds a given map layer to the map.layers list. It defaults to adding 
        the layer to the top of the map (end of list), but layer can be added
        to any location using the optional index argument.

        Args:
            new_layer (BaseLayer): The layer the add to map

        Optional Args:
            index (int): The index where to insert the new map layer.

        Returns:
            None
        """
        
        ## Call _activate on new_layer, a requirement for BaseLayer derivatives
        new_layer._activate(self)

        ## Add layer. 
        if index == -1:
            self.layers.append(new_layer)
        else:
            self.layers.insert(index, new_layer)
        

    def remove(self, del_layer):
        """
        Removes a given layer from the map.

        Removes a given layer from the maps layer list. Layer must exist in 
        map.layer for it to be removed, otherwise it throws an error.

        Args:
            del_layer (BaseLayer): The layer to remove from the Map. Must exist
            currently in map.layer.
        
        Returns:
            None
        """
        ## Call deactivate on del_layer
        del_layer._deactivate()
        self.layers.remove(del_layer)
    

    ##
    ## Reference System Methods
    ##
    
    def set_geographic_crs(self, new_crs):
        """
        Sets the base geographic reference system. 

        Sets the base geographic reference system, for accurate lat/lon to 
        projection conversion. Defaults to WGS84(EPSG:4326) 
        See: https://xkcd.com/2170/

        Args:
            new_crs (str | pyproj.crs.CRS): The CRS to use as the base 
            geographic reference system.
        
        Returns:
            None
        """

        if isinstance(new_crs, str):
            self.geographic_crs = pyproj.crs.CRS(new_crs)

        elif isinstance(new_crs, pyproj.crs.CRS):
            self.geographic_crs = pyproj.crs.CRS(new_crs)
        
        else:
            pass #@ NOTE: throw errors
     
        ## Recreate transformer objects
        self.transform_geo2proj = pyproj.Transformer.from_crs(self.geographic_crs, self.projected_crs, always_xy=True)
        self.transform_proj2geo = pyproj.Transformer.from_crs(self.projected_crs, self.geographic_crs, always_xy=True)


    def set_projection(self, new_crs): #@ Rename to set_crs
        """
        Sets the projected coordinate system of the map.

        Sets the projected coordinate system of the map. Or how the map 
        displays the spherical coordinates on a 2D plane.

        Args:
            new_crs (str | pyproj.crs.CRS): The CRS to use as the projected 
            reference system.
        
        Returns:
            None
        """

        #! NOTE: Get scale & keep it to change it to the correct scale 

        if isinstance(new_crs, str):
            self.projected_crs = pyproj.crs.CRS(new_crs)

        elif isinstance(new_crs, pyproj.crs.CRS):
            self.projected_crs = pyproj.crs.CRS(new_crs)
        
        else:
            print('error')
        
        ## Recreate transformer objects
        self.transform_geo2proj = pyproj.Transformer.from_crs(self.geographic_crs, self.projected_crs, always_xy=True)
        self.transform_proj2geo = pyproj.Transformer.from_crs(self.projected_crs, self.geographic_crs, always_xy=True)

    ##
    ## Location Methods
    ##
    
    def set_location(self, latitude, longitude):
        """
        Sets the geographic location of the map.

        Sets the geographic location of the center of the map, location is 
        specified using lat/lon, and stored as projection x/y.

        Args:
            latitude (float): The latitude coordinate of the map.
            longitude (float): The longitude coordinate of the map.

        Returns:
            None
        """
        geo_y, geo_x = latitude, longitude
        proj_x, proj_y = self.geo2proj(geo_x, geo_y)
        self.set_projection_coordinates(proj_x, proj_y)


    def get_location(self):
        """
        Returns the geographic location of the map.

        Returns the geographic location of the center of the map, location is
        returned in lat/lon.

        Args:
            None

        Returns:
            latitude (float): The latitude coordinate of the map.
            longitude (float): The longitude coordinate of the map.
        """
        geo_x, geo_y = self.proj2geo(self.proj_x, self.proj_y)
        latitude, longitude = geo_y, geo_x ## I do this for now
        return latitude, longitude


    def set_projection_coordinates(self, new_x, new_y):
        """
        Sets the projected location of the map.

        Sets the projected location of the center of the map, location is 
        specified and stored as projection x/y.

        Args:
            x (float): The x value of the projections coordinate of the map
            location.
            y (float): The y value of the projections coordinate of the map
            location.

        Returns:
            None
        """
        self.proj_x = new_x
        self.proj_y = new_y

    def get_projection_coordinates(self):
        """
        Returns the projected location of the map.

        Returns the projected location of the center of the map, location is 
        returned as x, y.

        Args:
            None

        Returns:
            x (float): The x value of the projections coordinate of the map
            location.
            y (float): The y value of the projections coordinate of the map
            location.
        """
        return self.proj_x, self.proj_y


    ##
    ## Scale Methods
    ##
    
    def set_scale(self, new_scale):
        """
        Set the scale of the map.

        Sets the scale of the map in meters per pixel. Scale is always in m/pix
        and thus is independent of the projections' base unit. This is done by 
        converting the m/pix scale to a internal projection scale.

        Args:
            new_scale (float): The new scale of the map in meters per pixel.

        Returns:
            None
        """

        ## Get unit code of base unit of projection
        proj_unit = self.projected_crs.axis_info[0].unit_code

        if proj_unit == '9003': ## 9003 == US survey foot
            ## Meters to feet
            new_scale = new_scale * 3.28084

        if proj_unit == '9122': ## 9122 == degree':
            ## degrees to meters
            new_scale = new_scale / 110570

        #@ NOTE: Add more units

        ## Set scale in proj units per pix
        self._proj_scale = float(new_scale)

    def get_scale(self):
        """
        Returns the map scale in meters per pixel.

        Returns the scale of the map in meters per pixel. Scale is always in 
        m/pix and thus is independent of the projections' base unit. This is 
        done by converting internal projection scale to the m/pix scale.

        Args:
            None

        Returns:
            scale (float): The scale of the map in meters per pixel.
        """
        ## Get current scale in units/pix
        proj_scale = self._proj_scale

        ## Get unit code of base unit of projection
        proj_unit = self.projected_crs.axis_info[0].unit_code

        if proj_unit == '9003': ## 9003 == US survey foot
            ## Meters to feet
            return proj_scale / 3.28084

        if proj_unit == '9122': ## 9122 == degree':
            ## meters to degrees
            return proj_scale * 110570

    ##
    ## Canvas Size Methods
    ##

    def set_size(self, width, height):
        """
        Sets the pixel size of the canvas.

        Sets the pixel width & height of the map area.

        Arguments:
            - width (int): the new width of the map canvas.
            - height (int): the new width of the map canvas.

        Returns: None
        """

        self.width = width
        self.height = height

    def get_size(self):
        """
        Returns the pixel size on the map canvas.

        Returns the width & height of the map area.

        Args:
            width (int): The width of the map canvas in pixels.
            height (int): The height of the map canvas in pixels.
            
        Returns:
            None
        """
        return self.width, self.height

    ##
    ## Backend, background, and rendering methods
    ##

    def set_renderer(self, renderer):
        """
        Tells the map which renderer to use to render the map.

        Sets the renderer to be used to render the map data. Set from a string 
        or a directly given renderer object.

        Args:
            renderer (str | base_renderer obj): A string naming the renderer to
            use, retrieved via the get_renderer function. Or a base_renderer 
            object to be used directly as the renderer.
            
        Returns:
            None
        """

        if isinstance(renderer, str):
            self.renderer = get_renderer(renderer)
        else: 
            self.renderer = renderer


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
        """
        Converts geographic coordinates to projection coordinates.
        """
        return self.transform_geo2proj.transform(geo_x, geo_y)
    
    def proj2geo(self, proj_x, proj_y):
        """
        Converts projection coordinates to geographic coordinates.
        """
        return self.transform_proj2geo.transform(proj_x, proj_y)


    def proj2pix(self, proj_x, proj_y):
        """
        Converts projection coordinates to pixel coordinates. 
        """
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
        """
        Converts canvas coordinates to projection coordinates.
        """
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
        """
        Converts geographic coordinates to canvas coordinates.
        """
        proj_x, proj_y = self.geo2proj(geo_x, geo_y)
        pix_x, pix_y = self.proj2pix(proj_x, proj_y)
        return pix_x, pix_y
    
    def pix2geo(self, pix_x, pix_y):
        """
        Converts canvas coordinates to geographic coordinates.
        """
        proj_x, proj_y = self.geo2proj(pix_x, pix_y)
        geo_x, geo_y = self.proj2pix(proj_x, proj_y)
        return geo_x, geo_y