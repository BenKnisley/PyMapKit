"""
Project: PyMapKit
Title: Map Class Definition
Function: Define Map class that PyMapKit project is build around.
Author: Ben Knisley [benknisley@gmail.com]
Created: 8 December, 2019
"""
import pyproj
import numpy as np
import warnings
from .backend import get_backend

class Map:
    """
    A class used to represent a map, and PyMapKit's central class.

    The Map class has three primary functions:
        - Store and manage map state: such as, location, projection, and scale
        - Hold and manage map layers added to it
        - Serve as entry point of rendering pipline
    """

    def __init__(self, projection="EPSG:3785", scale=50000.0, latitude=0.0, longitude=0.0, width=500, height=500, backend='pycairo'):
        """
        Initializes new Map object.
        
        Arguments:
            projection: Input defining which projection the map should use. Takes a string as either a EPSG code
            or a proj string. Also takes a pyproj.Proj object. Defaults to EPSG:4326.

            scale: Value indicating the scale of the map in meters per pixel. Takes an integer or a float. Defaults
            to 50000.

            latitude: The latitude to set the map to. Should be in WGS84. Defaults to 0 degrees.

            longitude: The longitude to set the map to. Should be in WGS84. Defaults to 0 degrees.

            width: The width in pixels of the map. Defaults to 500px. 

            height: The height in pixels of the map. Defaults to 500px.

            backend: The rendering backend to use. Defaults to PyCairo.
        """
        ## Keep an internal reference of WGS84 projection on hand
        ## For lat lon conversion
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

        ## Get backend from backend module
        self.renderer = get_backend(backend)

        ## Set projection coords from default or input lat, lon
        self._projx, self._projy = self.geo2proj(longitude, latitude)

    ###################
    ## Map Properties Methods
    ###################

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

    def set_scale(self, new_scale):
        """ 
        Sets the scale of the map

        Changes the scale of the map to the input value. Modifies both the _scale and _proj_scale properties. 

        Arguments:
            new_scale: 
                The scale to set the map to. Must be in meters per pixel regardless of the projection. Must be positive and non zero.

        Returns:
            None
        """
        ## Save m/pix scale into _scale before setting _proj_scale
        self._scale = new_scale

        ## Get projection crs dict, ignore all warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            crs_dict = self._projection.crs.to_dict()

        ## If units not defined in crs_dict the units are degrees
        if 'units' not in crs_dict:
            ## Convert scale to m/pix from deg
            new_scale = new_scale / 110570

        elif crs_dict['units'] == 'us-ft':
                new_scale = new_scale * 3.28084
        
        else:
            pass ## Is meters :) scale is already in m/pix
    
        ## Set processed newscale
        self._proj_scale = new_scale

    def get_scale(self):
        """ 
        Returns the current scale of the map.
        
        Returns the current scale of the map in meters per pixel.

        Arguments:
            None
        
        Returns:
            scale: The current scale of the map in meters per pixel.
        """
        return self._scale

    ################### 
    ## Layer Methods
    ###################

    def add_layer(self, new_map_layer, index=-1):
        """
        Adds a given map layer to the map

        Adds given layer to Maps' layer list, and calls layers' activate function.

        Arguments:
            new_map_layer: The layer to add to the Map layer list. Must be a MapLayer subclassed layer.

            optional:
            index: Index where the new layer should be added. Defaults to 0, top of list.
        
        Returns:
            None
        """
        ## Call new_map_layer activate function
        new_map_layer._activate(self)

        ## Add layer to layer_list
        if index == -1:
            self._layer_list.insert(len(self._layer_list), new_map_layer)
        else:
            self._layer_list.insert(index, new_map_layer)

    def remove_layer(self, layer):
        """ 
        Removes a specific map layer from the map
        
        Removes the given map layer, or layer at given index, and then runs layers' deactivate method.

        Arguments:
            layer: The MapLayer to remove.
            or
            index: The index of the layer to remove.
        
        Returns:
            none
        """

        ## If input layer is an integer, assume input is index
        if isinstance(layer, int):
            ## Pop off layer at index, and call deactivate method
            layer = self._layer_list.pop(layer)
            layer._deactivate()
        else:
            ## Remove layer, and call deactivate method
            self._layer_list.remove(layer)
            layer._deactivate()
        
        ## c

    def get_layer(self, index):
        """ 
        Returns a map layer
        
        Returns the MapLayer Object at the given index, without removing it.

        Arguments:
            index: The index of the layer to return.

        Returns:
            MapLayer object at given index
        """
        ## Look up layer at index and return it 
        layer = self._layer_list[index]
        return layer

    ################### 
    ## Rendering Methods
    ###################

    def set_size(self, new_width, new_height): # size tuple (width, height)
        """ 
        Changes the size of the map drawing area.

        Sets the pixel width and height of the drawing area to the given values. 

        Arguments:
            new_width: 
                The width to set the drawing area to. Must be a positive integer.
            new_height: 
                The height to set the drawing area to. Must be a positive integer.

        Returns:
            None
        """
        self._width = new_width
        self._height = new_height

    def get_size(self):
        """ 
        Returns the current size of the map drawing area.
        
        Returns the current pixel width and height of the map drawing area.

        Arguments:
            None
        
        Returns:
            width:
                The current width of the map drawing area.
            height: 
                 The current height of the map drawing area.
        """
        return self._width, self._height
    
    @property
    def width(self):
        """
        Canvas width property
        
        Get or set the pixel width of the map canvas.
        
        Arguments:
            optional (as setter):
            new_width: the new width of the map canvas.
        
        Returns:
            optional (as getter):
            width: the current width of the map canvas.
        """
        return self._width

    @width.setter
    def width(self, new_width):
        self._width = new_width
    
    @property
    def height(self):
        """
        Canvas height property
        
        Get or set the pixel height of the map canvas.
        
        Arguments:
            optional (as setter):
            new_height: the new height of the map canvas.
        
        Returns:
            optional (as getter):
            height: the current height of the map canvas.
        """
        return self._height

    @height.setter
    def height(self, new_height):
        self._height = new_height
  
    def get_canvas_center(self): #! TODO: Make _ method
        """ 
        Returns the pixel at the center of the map canvas

        Returns the pixel coordinate of the point that is at the center of the canvas.
        
        Arguments:
            None
        
        Returns:
            (pix_x, pix_y): A tuple with the x value and y value of the center pixel
        """
        pix_x = int(self._width / 2)
        pix_y = int(self._height / 2)

        #! TODO: Make return two values
        return (pix_x, pix_y)

    def set_background_color(self, color_input):
        """
        Sets the background color of map
        
        Sets the background color of map from user defined color.

        Arguments:
            color_input: A color name string, color hex string, or set of values 
            defining the color to set the map background to. Valid inputs include:
            'lightblue', '#11c155', (0.1, 0.45, 0.1), and (34, 123, 32).
        
        Returns:
            None
        """
        ## Set color value
        self._background_color = color_input

    def set_backend(self, backend):
        """
        Changes the current rendering backend of the map.

        Sets the rendering backend of the map to the backend associated with the users input.
        
        This method calls get_backend function in PyMapKit's backend submodule. The get_backend 
        function will import only the required backend modules, and will then return a usable 
        backend object. See docs for PyMapKit.backend.get_backend for more info.
        
        Arguments:
            backend: A string representing the backend to use. Or the actual backend object to use.

        Returns:
            None
        """
        ## Set renderer to result of .backend.get_backend
        self.renderer = get_backend(backend)

    def render(self, target=None):
        """
        Renders the map

        Renders the map with the current backend to the given target. The entrypoint of the 
        rendering pipeline. Draws map background, then passes renderer to each MapLayer in
        map_layer_list.

        Arguments:
            optional:
                target: The destination of the final rendered map. Can be a backend canvas, or
                    path of a output file. 

                    - target=None: If no target is given; render will still run as normal but 
                        no output is guaranteed.(Tk backend will show map on a window, cairo 
                        backend will not). 
                    
                    - target=canvas: If a canvas the backend can draw on is given; render will
                        draw map on that object.

                    - target=path: If a path string is given: backend will create a new canvas,
                        draw map onto that, and save result to image at given path. 
        Returns:
            None
        """
        output_file = None
        
        if self.renderer.can_render_to(target):
            canvas = target
        else:
           canvas = self.renderer.create_canvas(self.width, self.height)
           output_file = target
        
        ## If not None
        if self._background_color:
            ## Draw background
            self.renderer.draw_background(canvas, self._background_color)

        ## Draw each layer, pass renderer, and canvas to each object
        for layer in self._layer_list:
            layer.draw(self.renderer, canvas)
        
        ## Save or display canvas
        self.renderer.save(canvas, output_file)
    

    ###################
    ## Projection Transformation Methods
    ###################

    def geo2proj(self, geo_x, geo_y):
        """
        Convert geographic coordinates to projection coordinates

        Converts given geographic coordinates into the corresponding projection coordinates of the 
        current map's projection. Input data can be pairs of ints, floats, lists, or NumPy arrays.
        Output type matches input, except Python list returns a NumPy array.

        Arguments:
            geo_x: The x value(s) (Longitude) of the geographic coordinate(s). Can be an int, float, list, or
                NumPy array.

            geo_y: The y value(s) (Latitude) of the geographic coordinate(s). Can be an int, float, list, or
                NumPy array.
        
        Returns:
            proj_x: The x value(s) of the projected coordinate(s). Depending on input, returns int, float, or
                NumPy array.

            proj_y: The y value(s) of the projected coordinate(s). Depending on input, returns int, float, or
                NumPy array.
        """
        ## If current map projection is WGS84: No projection is needed, return input unchanged
        if self._projection == self._WGS84:
            return geo_x, geo_y

        ## If input data is a single data pair: transform and return singlet values
        if isinstance(geo_x, int) or isinstance(geo_x, float):
            proj_x, proj_y = pyproj.transform(self._WGS84, self._projection, geo_y, geo_x)
            return proj_x, proj_y

        ## If input is a python list: convert to numpy arrays before processing
        if isinstance(geo_x, list):
            geo_x = np.array(geo_x)
            geo_y = np.array(geo_y)

        ## Project geographic numpy arrays to projection numpy arrays
        proj_x, proj_y = pyproj.transform(self._WGS84, self._projection, geo_y, geo_x)

        ## Replace all np.inf values with last real value (to prevent tearing during rendering)
        while np.isinf(proj_x).any():
            proj_x[np.where(np.isinf(proj_x))] = proj_x[np.where(np.isinf(proj_x))[0]-1]
            proj_y[np.where(np.isinf(proj_y))] = proj_y[np.where(np.isinf(proj_y))[0]-1]

        ## Return projected np arrays
        return proj_x, proj_y

    def proj2geo(self, proj_x, proj_y):
        """
        Convert projection coordinates to geographic coordinates

        Converts given projection coordinates into WGS86 geographic coordinates. 
        Input data can be pairs of ints, floats, lists, or NumPy arrays.
        Output type matches input, except Python list returns a NumPy array.

        Arguments:
            proj_x: The x value(s) of the projected coordinate(s). Can be an int, float, list, or
                NumPy array.

            proj_y: The y value(s) of the projected coordinate(s). Can be an int, float, list, or
                NumPy array.
        
        Returns:
            geo_x: The x value(s) (Longitude) of the geographic coordinate(s). Depending on input, returns int, float, or
                NumPy array.

            geo_y: The y value(s) (Latitude) of the geographic coordinate(s). Depending on input, returns int, float, or
                NumPy array.
        """
        ## If dest_proj is WGS84, no convert is needed, pass input to output
        if self._WGS84 == self._projection:
            return proj_x, proj_y

        ## If input data is a single data pair: transform and return singlet values
        if isinstance(proj_x, int) or isinstance(proj_x, float):
            lat, lon = pyproj.transform(self._projection, self._WGS84, proj_x, proj_y)
            return lon, lat

        ## If input is a python list: convert to numpy arrays before processing
        if isinstance(proj_x, list):
            proj_x = np.array(proj_x)
            proj_y = np.array(proj_y)

        ## Project geographic numpy arrays to projection numpy arrays
        lat, lon = pyproj.transform(self._projection, self._WGS84, proj_x, proj_y)

        return lon, lat

    def proj2pix(self, proj_x, proj_y):
        """
        Convert projection coordinates to pixel coordinates

        Converts given projection coordinates into pixel coordinates based around
        geographic location and scale of map. Where the geographic location of map 
        is the center of the map canvas. Input data can be pairs of ints, floats, 
        lists, or NumPy arrays. Output type matches input, except Python list returns
        a NumPy array.

        Arguments:
            proj_x: The x value(s) of the projected coordinate(s). Can be an int, float, list, or
                NumPy array.

            proj_y: The y value(s) of the projected coordinate(s). Can be an int, float, list, or
                NumPy array.
        
        Returns:
            pix_x: The x value(s) of the pixel coordinate(s). Depending on input, returns int, float, or
                NumPy array.

            pix_y: The y value(s) of the pixel coordinate(s). Depending on input, returns int, float, or
                NumPy array.
        """
        ## Unpack importent points
        focusX, focusY = self._projx, self._projy
        centerX, centerY = self.get_canvas_center()

        ## If input is a Python list, convert to NumPy array
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

        ## Return pixel coord values
        return pix_x, pix_y

    def pix2proj(self, pix_x, pix_y):
        """
        Convert pixel coordinates to projection coordinates

        Converts given pixel coordinates into projection coordinates based around
        current projection, location and scale of map. Where the geographic location 
        of map is the center of the map canvas. Input data can be pairs of ints, floats, 
        lists, or NumPy arrays. Output type matches input, except Python list returns
        a NumPy array.

        Arguments:
            pix_x: The x value(s) of the pixel coordinate(s). Can be an int, float, list, or
                NumPy array.

            pix_y: The y value(s) of the pixel coordinate(s). Can be an int, float, list, or
                NumPy array.
        
        Returns:
            proj_x: The x value(s) of the projected coordinate(s). Depending on input, returns int, float, or
                NumPy array.

            proj_y: The y value(s) of the projected coordinate(s). Depending on input, returns int, float, or
                NumPy array.
        """
        ## Unpack points
        focus_x, focus_y = self._projx, self._projy
        center_x, center_y = self.get_canvas_center()

        ## If Python list, convert to NumPy Array
        if isinstance(pix_x, list):
            pix_x = np.array(pix_x)
            pix_y = np.array(pix_y)

        ## Convert pixel values to projections values
        proj_x = focus_x + ((pix_x - center_x) * float(self._proj_scale)) 
        #proj_y = 0 - (focus_y + ((pix_y - center_y) * float(self._proj_scale)) ) ## Fixed
        proj_y = (focus_y + ((pix_y - center_y) * float(self._proj_scale)) )

        ## Return projection values
        return proj_x, proj_y

    def geo2pix(self, geo_x, geo_y):
        """
        Convert geographic coordinates to pixel coordinates

        Converts given geographic coordinates into pixel coordinates based around
        current projection, location and scale of map. This method just dumps input
        directly through geo2proj & proj2pix, so no optimization should be expected.
        Input data can be pairs of ints, floats, lists, or NumPy arrays. Output type
        matches input, except Python list returns a NumPy array.

        Arguments:
            geo_x: The x value(s) (Longitude) of the geographic coordinate(s). Can be an int, float, list, or
                NumPy array.

            geo_y: The y value(s) (Latitude) of the geographic coordinate(s). Can be an int, float, list, or
                NumPy array.
        
        Returns:
            pix_x: The x value(s) of the pixel coordinate(s). Depending on input, returns int, float, or
                NumPy array.

            pix_y: The y value(s) of the pixel coordinate(s). Depending on input, returns int, float, or
                NumPy array.
        """
        ## Daisy chain geo2proj and proj2pix
        proj_x, proj_y = self.geo2proj(geo_x, geo_y)
        pix_x, pix_y = self.proj2pix(proj_x, proj_y)
        return pix_x, pix_y

    def pix2geo(self, pix_x, pix_y):
        """
        Convert pixel coordinates to geographic coordinates

        Converts given pixel coordinates into geographic coordinates based around
        current projection, location and scale of map. This method just dumps input
        directly through pix2proj & proj2geo, so no optimization should be expected.
        Input data can be pairs of ints, floats, lists, or NumPy arrays. Output type
        matches input, except Python list returns a NumPy array.

        Arguments:
            pix_x: The x value(s) of the pixel coordinate(s). Depending on input, returns int, float, or
                NumPy array.

            pix_y: The y value(s) of the pixel coordinate(s). Depending on input, returns int, float, or
                NumPy array.
            
        Returns:
            geo_x: The x value(s) (Longitude) of the geographic coordinate(s). Can be an int, float, list, or
                NumPy array.

            geo_y: The y value(s) (Latitude) of the geographic coordinate(s). Can be an int, float, list, or
                NumPy array.
        """
        ## Daisy chain pix2proj and proj2geo
        proj_x, proj_y = self.pix2proj(pix_x, pix_y)
        geoPoint = self.proj2geo(proj_x, proj_y)
        return geoPoint

