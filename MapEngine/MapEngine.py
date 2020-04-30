#!/usr/bin/env python3
"""
Title: MapEngine Class Definition
Project: MapEngine
Function: Define MapEngine class and all methods.
Created: 8 December, 2019
Author: Ben Knisley [benknisley@gmail.com]
"""
import pyproj
import numpy as np
import warnings


class MapEngine:
    """
    A class to manage map layers, state, and rendering.
    #
    Attributes:
        add_layer: Adds a MapLayer subclassed layer to layer list.
        remove_layer: Removes a layer from layer list.
        get_layer: Returns (but does not remove) layer in layer list.
        ...
    """

    def __init__(self, projection="EPSG:4326", scale=50000.0, latitude=0.0, longitude=0.0, width=500, height=500):
        """
        Initializes new MapEngine object.
        
        Arguments:
            projection: Input defining which projection the map should use. Takes a string as either a EPSG code
            or a proj string. Also takes a pyproj.Proj object. Defaults to EPSG:4326.

            scale: Value indicating the scale of the map in meters per pixel. Takes an integer or a float. Defaults
            to 50000.

            latitude: The latitude to set the map to. Should be in WGS84. Defaults to 0 degrees.

            longitude: The longitude to set the map to. Should be in WGS84. Defaults to 0 degrees.

            width: The width in pixels of the map. Defaults to 500px. 

            height: The height in pixels of the map. Defaults to 500px.
        """
        ## Keep an internal reference WGS84 projection on hand
        self._WGS84 = pyproj.Proj("EPSG:4326")

        ## Create list to hold MapLayers
        self._layer_list = []

        ## Set default background color
        self.set_background_color('#0C0C0C')

        ## Set Projection from default or input
        self._projection = pyproj.Proj(projection)
        
        ## set _scale and _proj_scale from defalt or input
        self._scale = scale
        self.set_scale(scale) 
        
        ## Set private map width and height from defalt or input
        self._width = width
        self._height = height

        ## Set projection coords from default or input lat, lon
        self._projx, self._projy = self.geo2proj(longitude, latitude)
        
    def add_layer(self, new_map_layer, index=0):
        """
        Adds a map layer

        Adds given layer to MapEngines' layer list, and calls layers' activate function.

        Arguments:
            new_map_layer: The layer to add to the MapEngine layer list. Must be a MapLayer subclassed layer.

            index: Index where the new layer should be added. Defaults to 0, top of list.
        
        Returns:
            None
        """
        ## Call new_map_layer activate function
        new_map_layer._activate(self)

        ## Add layer to layer_list
        self._layer_list.insert(index, new_map_layer) 

    def remove_layer(self, index):
        """ 
        Removes a map layer
        
        Removes layer at given index, and runs layers' deactivate method.

        Arguments:
            index: The index of the layer to remove.
        
        Returns:
            none
        """
        ## Pop off layer at index, and call deactivate method
        layer = self._layer_list.pop(index)
        layer._deactivate()

    def get_layer(self, index):
        """ 
        Returns a map layer
        
        Returns the MapLayer Object at the given index, with removing it.

        Arguments:
            index: The index of the layer to return.

        Returns:
            MapLayer object at given index
        """
        ## Look up layer at index and return it 
        layer = self._layer_list[index]
        return layer

    def get_projection(self):
        """ 
        Gets the current projection 

        Gets the string representative of the current projection.

        Arguments:
            None

        Returns:
            Returns the string representative of the current projection
        """
        return self._projection.srs

    def set_projection(self, new_projection):
        """ 
        Sets the current projection 

        Sets the projection from a pyproj Proj object or a string representative 
        of a projection. EPSG code or proj string.

        Arguments:
            new_projection: The string representative of the new projection, or a Proj object.

        Returns:
            None
        """
        ## Get coordinates before changing projection
        lat, lon = self.get_location()

        ## Set projection according input str or Proj object
        if isinstance(new_projection, str):
            self._projection = pyproj.Proj(new_projection)
        else:
            self._projection = new_projection

        ## Reset scale and location on projection change
        self.set_location(lat, lon)
        self.set_scale(self._scale)

        ## Call activate of all layers to reset projection
        for layer in self._layer_list:
            layer._activate(self)

    def set_proj_coordinate(self, new_proj_x, new_proj_y):
        """ 
        Sets the projection coordinates

        Sets the projection coordinates from the given values.
        This should most often be used by tools changing location
        without having go through projection.

        Arguments:
            new_proj_x: The new x value to move the map too
            new_proj_y: The new y value to move the map too

        Returns:
            None
        """
        self._projx = new_proj_x
        self._projy = new_proj_y

    def get_proj_coordinate(self):
        """ 
        Gets the current projection coordinates

        Returns the current location in coordinates of the current projection.

        Arguments:
            None:

        Returns:
            project_x: The current projection x value of the map
            project_y: The current projection y value of the map
        """
        return self._projx, self._projy

    def set_location(self, new_lat, new_long):
        """ 
        Sets geographic location on map 
        
        Sets new map location from given geographic coordinates.
        Input locations are in WGS86.

        Arguments:
            new_lat: The latitude to move the map to.
            new_long: The longitude to move the map to.

        Returns:
            None
        """
        ## Set the projection coord via the geo2proj method
        self._projx, self._projy = self.geo2proj(new_long, new_lat)

    def get_location(self):
        """ 
        Returns the current geographic location of the map
        
        Gets the geographic location on the map from the stored
        projection coordinates.

        Arguments:
            None
        
        Returns:
            latitude: The current latitude of the map.
            longitude: The currnt longitude on the map.
        """
        lon, lat = self.proj2geo(self._projx, self._projy)
        return lat, lon
    
    @property
    def longitude(self):
        """ 
        Longitude getter property
        
        Returns the current geographic longitude of the center on the map.
        
        Arguments:
            None
        
        Returns:
            longitude: The current longitude of the map.
        """
        return self.get_location()[1]

    @longitude.setter
    def longitude(self, new_long):
        """ 
        Longitude setter property
        
        Sets the current geographic longitude of the center on the map.
        
        Arguments:
            new_long: The new longitude of the map.
        
        Returns:
            None
        """
        self.set_location(self.get_location()[0], new_long)


    @property
    def latitude(self):
        """ 
        Latitude getter property
        
        Returns the current geographic latitude of the center on the map.
        
        Arguments:
            None
        
        Returns:
            latitude: The current longitude of the map.
        """
        return self.get_location()[0]
    
    @latitude.setter
    def latitude(self, new_lat):
        """ 
        Latitude setter property
        
        Sets the current geographic latitude of the center on the map.
        
        Arguments:
            new_lat: The new latitude of the map.
        
        Returns:
            None
        """
        self.set_location(new_lat, self.get_location()[1])

    """
    ============================================
    Write docs and tests for following functions
    ============================================
    """

    ## Scale methods
    def set_scale(self, new_scale):
        """ """
        ## Set _scale before setting _proj_scale
        self._scale = new_scale

        ## Get projection crs dict, ignore all warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            crs_dict = self._projection.crs.to_dict()

        if 'units' not in crs_dict:
            ## Convert scale to m/pix from deg
            new_scale = new_scale / 110570
        else: 
            if crs_dict['units'] == 'us-ft':
                new_scale = new_scale * 3.28084
            else:
                pass ## Is meters :)
        
        ## Set processed newscale
        self._proj_scale = new_scale

    def get_scale(self):
        return self._scale

    ## Size methods
    def set_size(self, new_width, new_height): # size tuple (width, height)
        """ Sets size of  """
        assert isinstance(new_width, int)
        assert isinstance(new_height, int)
        assert new_height > 0
        assert new_width > 0

        self._width = new_width
        self._height = new_height

    def get_size(self):
        """ """
        return self._width, self._height
    
    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, new_width):
        assert isinstance(new_width, int)
        self._width = new_width
    
    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, new_height):
        assert isinstance(new_height, int)
        self._height = new_height
  
    def get_canvas_center(self):
        """ Returns a pixel point that is the center of the canvas. """
        x = int(self._width/2)
        y = int(self._height/2)
        return (x, y)

    ## Drawing and style methods
    def render(self, renderer, cr):
        """ """
        ## Draw background by drawing rectangle the size of canvas
        renderer.draw_background(cr, self._background_color)

        ## Draw each layer, pass renderer, and canvas to each object
        for layer in self._layer_list:
            layer.draw(renderer, cr)

    def set_background_color(self, input_color):
        """
        Sets background color of map.
        ...
        """
        ## Set RGB values
        self._background_color = input_color


    ## Geo Functions
    def geo2proj(self, geo_x, geo_y):
        """
        Good
        """
        ## If dest_proj is WGS84, no convert is needed, pass geo_data to output
        if self._WGS84 == self._projection:
            return geo_x, geo_y

        if isinstance(geo_x, int) or isinstance(geo_x, float):
            proj_x, proj_y = pyproj.transform(self._WGS84, self._projection, geo_y, geo_x)
            return proj_x, proj_y

        if isinstance(geo_x, list):
            geo_x = np.array(geo_x)
            geo_y = np.array(geo_y)

        proj_x, proj_y = pyproj.transform(self._WGS84, self._projection, geo_y, geo_x)

        ## Replace all inf with last good value
        while np.isinf(proj_x).any():
            proj_x[np.where(np.isinf(proj_x))] = proj_x[np.where(np.isinf(proj_x))[0]-1]
            proj_y[np.where(np.isinf(proj_y))] = proj_y[np.where(np.isinf(proj_y))[0]-1]

        return proj_x, proj_y

    def proj2geo(self, proj_x, proj_y):
        """ """
        ## If dest_proj is WGS84, no convert is needed, pass input to output
        if self._WGS84 == self._projection:
            return proj_x, proj_y

        ## Convert proj coords to geo coord and return
        lat, lon = pyproj.transform(self._projection, self._WGS84, proj_x, proj_y)
        return lon, lat

    def proj2pix(self, proj_x, proj_y):
        """ """
        ## Unpack points
        focusX, focusY = self._projx, self._projy
        centerX, centerY = self.get_canvas_center()

        if isinstance(proj_x, list):
            ## Convert lists of points to numpy arrays
            proj_x = np.array(proj_x)
            proj_y = np.array(proj_y)

        #proj_x = np.round(proj_x, decimals=2)
        #proj_y = np.round(proj_y, decimals=2)

        ## Do math logic on all points
        pix_x = ((proj_x - focusX) / float(self._proj_scale)) + centerX
        pix_y = -((proj_y - focusY) / float(self._proj_scale)) + centerY

        ## Round to int to make drawing faster
        pix_x = np.rint(pix_x).astype(int)
        pix_y = np.rint(pix_y).astype(int)

        return pix_x, pix_y

    def pix2proj(self, pix_x, pix_y):
        """ """
        ## Unpack points
        focus_x, focus_y = self._projx, self._projy
        center_x, center_y = self.get_canvas_center()

        if isinstance(pix_x, list):
            ## Convert lists of points to numpy arrays
            pix_x = np.array(pix_x)
            pix_y = np.array(pix_y)

        ##
        proj_x = ((pix_x - center_x) * self._proj_scale) + focus_x
        proj_y = ((pix_y - center_y) * self._proj_scale) + focus_y

        return proj_x, proj_y

    def geo2pix(self, geo_x, geo_y):
        """ """
        proj_x, proj_y = self.geo2proj(geo_x, geo_y)
        pix_x, pix_y = self.proj2pix(proj_x, proj_y)
        return pix_x, pix_y

    def pix2geo(self, pixPoint):
        """ """
        projPoint = self.pix2proj(pixPoint[0], pixPoint[1])
        geoPoint = self.proj2geo(projPoint[0], projPoint[1])
        return geoPoint

