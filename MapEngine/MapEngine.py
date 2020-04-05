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

        ## Keep a reference WGS84 projection on hand
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
        
        ## Set map width and height from defalt or input
        self._width = width
        self._height = height

        ## Set projection coords from default or input lat, lon
        self._projx, self._projy = self.geo2proj(longitude, latitude)
        
    ## Layer methods
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

    """
    #
    Write docs and tests for following functions
    #
    """

    ## Projection methods
    def get_projection(self):
        """ """
        return self._projection

    def set_projection(self, new_projection):
        """ """
        lat, lon = self.get_location()

        if isinstance(new_projection, str):
            self._projection = pyproj.Proj(new_projection)

        else: ## PyProj object TODO: Check that it is PyProj object
            self._projection = new_projection

        ## Reset scale and location on projection change
        self.set_location(lat, lon)
        self.set_scale(self._scale)

        for layer in self._layer_list:
            layer._activate(self)
        
    ## Location methods
    def set_proj_coordinate(self, new_proj_x, new_proj_y):
        """ Sets projection location of map  """
        self._projx = new_proj_x
        self._projy = new_proj_y

    def get_proj_coordinate(self):
        """ Returns the projection location """
        return self._projx, self._projy

    def set_location(self, new_lat, new_long): #Y,X
        """ Sets geographic location on map """
        #! Add constaints
        self._projx, self._projy = self.geo2proj(new_long, new_lat) ## Y,X

    def get_location(self):
        """ Returns the geographic location on map """
        lon, lat = self.proj2geo(self._projx, self._projy)
        return lat, lon
    
    @property
    def longitude(self):
        return self.get_location()[1]

    @longitude.setter
    def longitude(self, new_long):
        self.set_location(self.get_location()[0], new_long)

    @property
    def latitude(self):
        return self.get_location()[0]
    
    @latitude.setter
    def latitude(self, new_lat):
        self.set_location(new_lat, self.get_location()[1])

    ## Scale methods
    def set_scale(self, new_scale):
        """ """
        ## Set _scale before setting _proj_scale
        self._scale = new_scale


        if 'units' not in self._projection.crs.to_dict():
            ## Convert scale to m/pix from deg
            new_scale = new_scale / 110570
        else: 
            if self._projection.crs.to_dict()['units'] == 'us-ft':
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
        self._background_color = _color_converter(input_color)


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
        ## If dest_proj is WGS84, no convert is needed, pass geo_data to output
        if self._WGS84 == self._projection:
            return proj_x, proj_y


        lat, lon = pyproj.transform(self._projection, self._WGS84, proj_x, proj_y)
        #geo_data = (lat, lon)
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

    def geo2pix(self, geoPoint):
        """ """
        projPoint = self.geo2proj(geoPoint[0], geoPoint[1])
        pixPoint = self.proj2pix(projPoint[0], geoPoint[1])
        return pixPoint

    def pix2geo(self, pixPoint):
        """ """
        projPoint = self.pix2proj(pixPoint[0], pixPoint[1])
        geoPoint = self.proj2geo(projPoint[0], projPoint[1])
        return geoPoint


def _color_converter(input_color):
    """ Converts different color formats into single format.

    Inputs:
        - (float, float, float) - A tuple of three floats between 0.0 and 1.0
            representing red, green, & blue values respectively.

        - (int, int, int) - A tuple of three ints between 0 and 1
            representing red, green, & blue values respectively.

        - "#0F0F0F" - A html color hex string.

        - "colorname" - A html color name.

    Returns:
        - (float, float, float) - A tuple of three floats between 0.0 and 1.0
            representing red, green, & blue values respectively.

    """
    ## Two tuple types, 0-1 or 0-256
    if isinstance(input_color, tuple):

        ## If float tuple, input same as output
        if isinstance(input_color[0], float):
            return input_color

        if isinstance(input_color[0], int):
            R = input_color[3] / 255.0
            G = input_color[5] / 255.0
            B = input_color[7] / 255.0
            return (R,G,B)

    ## Two types of color strings: Html color names and hex
    if isinstance(input_color, str):
        ## Define color dictionary, with html color names defined
        color_dict = {"aliceblue": "#f0f8ff", "antiquewhite": "#faebd7", "aqua": "#00ffff", "aquamarine": "#7fffd4", "azure": "#f0ffff", "beige": "#f5f5dc", "bisque": "#ffe4c4", "black": "#000000", "blanchedalmond": "#ffebcd", "blue": "#0000ff", "blueviolet": "#8a2be2", "brown": "#a52a2a", "burlywood": "#deb887", "cadetblue": "#5f9ea0", "chartreuse": "#7fff00", "chocolate": "#d2691e", "coral": "#ff7f50", "cornflowerblue": "#6495ed", "cornsilk": "#fff8dc", "crimson": "#dc143c", "cyan": "#00ffff", "darkblue": "#00008b", "darkcyan": "#008b8b", "darkgoldenrod": "#b8860b", "darkgray": "#a9a9a9", "darkgreen": "#006400", "darkkhaki": "#bdb76b", "darkmagenta": "#8b008b", "darkolivegreen": "#556b2f", "darkorange": "#ff8c00", "darkorchid": "#9932cc", "darkred": "#8b0000", "darksalmon": "#e9967a", "darkseagreen": "#8fbc8f", "darkslateblue": "#483d8b", "darkslategray": "#2f4f4f", "darkturquoise": "#00ced1", "darkviolet": "#9400d3", "deeppink": "#ff1493", "deepskyblue": "#00bfff", "dimgray": "#696969", "dodgerblue": "#1e90ff", "firebrick": "#b22222", "floralwhite": "#fffaf0", "forestgreen": "#228b22", "fuchsia": "#ff00ff", "gainsboro": "#dcdcdc", "ghostwhite": "#f8f8ff", "gold": "#ffd700", "goldenrod": "#daa520", "gray": "#808080", "green": "#008000", "greenyellow": "#adff2f", "honeydew": "#f0fff0", "hotpink": "#ff69b4", "indianred": "#cd5c5c", "indigo": "#4b0082", "ivory": "#fffff0", "khaki": "#f0e68c", "lavender": "#e6e6fa", "lavenderblush": "#fff0f5", "lawngreen": "#7cfc00", "lemonchiffon": "#fffacd", "lightblue": "#add8e6", "lightcoral": "#f08080", "lightcyan": "#e0ffff", "lightgoldenrodyellow": "#fafad2", "lightgray": "#d3d3d3", "lightgreen": "#90ee90", "lightpink": "#ffb6c1", "lightsalmon": "#ffa07a", "lightseagreen": "#20b2aa", "lightskyblue": "#87cefa", "lightslategray": "#778899", "lightsteelblue": "#b0c4de", "lightyellow": "#ffffe0", "lime": "#00ff00", "limegreen": "#32cd32", "linen": "#faf0e6", "magenta": "#ff00ff", "maroon": "#800000", "mediumaquamarine": "#66cdaa", "mediumblue": "#0000cd", "mediumorchid": "#ba55d3", "mediumpurple": "#9370d8", "mediumseagreen": "#3cb371", "mediumslateblue": "#7b68ee", "mediumspringgreen": "#00fa9a", "mediumturquoise": "#48d1cc", "mediumvioletred": "#c71585", "midnightblue": "#191970", "mintcream": "#f5fffa", "mistyrose": "#ffe4e1", "moccasin": "#ffe4b5", "navajowhite": "#ffdead", "navy": "#000080", "oldlace": "#fdf5e6", "olive": "#808000", "olivedrab": "#6b8e23", "orange": "#ffa500", "orangered": "#ff4500", "orchid": "#da70d6", "palegoldenrod": "#eee8aa", "palegreen": "#98fb98", "paleturquoise": "#afeeee", "palevioletred": "#db7093", "papayawhip": "#ffefd5", "peachpuff": "#ffdab9", "peru": "#cd853f", "pink": "#ffc0cb", "plum": "#dda0dd", "powderblue": "#b0e0e6", "purple": "#800080", "red": "#ff0000", "rosybrown": "#bc8f8f", "royalblue": "#4169e1", "saddlebrown": "#8b4513", "salmon": "#fa8072", "sandybrown": "#f4a460", "seagreen": "#2e8b57", "seashell": "#fff5ee", "sienna": "#a0522d", "silver": "#c0c0c0", "skyblue": "#87ceeb", "slateblue": "#6a5acd", "slategray": "#708090", "snow": "#fffafa", "springgreen": "#00ff7f", "steelblue": "#4682b4", "tan": "#d2b48c", "teal": "#008080", "thistle": "#d8bfd8", "tomato": "#ff6347", "turquoise": "#40e0d0", "violet": "#ee82ee", "wheat": "#f5deb3", "white": "#ffffff", "whitesmoke": "#f5f5f5", "yellow": "#ffff00", "yellowgreen": "#9acd32"}

        if input_color.lower() in color_dict:
            input_color = color_dict[input_color.lower()]


        if '#' in input_color and len(input_color) == 7:
            ## Hex string color
            R = int(input_color[1:3], 16) / 255.0
            G = int(input_color[3:5], 16) / 255.0
            B = int(input_color[5:7], 16) / 255.0
            return (R,G,B)
