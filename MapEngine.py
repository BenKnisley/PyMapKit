#!/usr/bin/env python3
"""
Project: Map Engine
Title: MapEngine
Author: Ben Knisley [benknisley@gmail.com]
Date: 8 December, 2019
Function:
"""
## Import PyProj, and numpy
import pyproj
from pyproj import Transformer, transform
import numpy as np

## Import MapLayer and style
import MapEngine.GeoFunctions as GeoFunctions
import MapEngine.CairoMapPainter as CairoMapPainter


def color_converter(input_color):
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


class MapEngine:
    """A class to manage map infomation, layers, and drawing."""
    def __init__(self, **input_args):
        """
        Initializes MapEngine object.

        Input: None required
        Optional:
            - projection - the projection string of the projection to use.
                Defaults to EPSG:4326.

            - coordinate - the starting geographic location to use. Defaults to
                Lat:0.0 Lon:0.0

            - scale - the starting scale to use. Defaults to 0.01

        Results: A new MapEngine object.
        Returns: None
        """
        ## Keep a reference WGS84 projection on hand
        self._WGS84 = pyproj.Proj("EPSG:4326")

        ## Create list to hold MapLayers
        self._layer_list = []

        ## Get projection string from input_args, or default to WGS84
        if "projection" in input_args:
            projection_str = input_args["projection"]
        else:
            projection_str = "EPSG:4326"
        ## Create and set PyProj projection
        self._projection = pyproj.Proj(projection_str)

        if "coordinate" in input_args:
            initCoord = input_args["coordinate"]
        else:
            initCoord = (0,0)
        ## Set point of intrest
        self._POI = self.geo2proj(initCoord)

        if "scale" in input_args:
            scale = input_args["scale"]
        else:
            scale = 0.01
        ## Set point of intrest
        self._scale = scale

        ## Set default canvas size
        self._size = (500, 500) ## Default to 500px x 500px

        ## Create MapPainter object
        self._map_painter = CairoMapPainter.CairoMapPainter()

        ## Set default background color
        self._background_color = (0.05, 0.05, 0.05)

    ## Drawing and style methods
    def draw(self, cr):
        """
        Draws the map on canvas.

        Input: cr - a cairo canvas object

        Result: The background and all map layers are drawn onto the canvas.

        Returns: None
        """
        ## Draw background by drawing rectangle the size of canvas
        cr.set_source_rgb(*self._background_color)
        cr.rectangle( 0,0, self._size[0], self._size[1] ) ## Draw rectangle over entire widget
        cr.fill() ## Fill rectangle

        ## Draw each layer
        for layer in self._layer_list:
            layer.draw(cr)

    def set_background_color(self, input_color):
        """
        Sets background color of map.
        ...
        """

        self._background_color = color_converter(input_color)



    ## Layer methods
    def add_layer(self, new_map_layer):
        """
        Activates and adds a new layer to MapEngine
        """
        ## Call new_map_layer activate function
        new_map_layer._activate(self)

        ## Add layer to layer_list
        self._layer_list.append(new_map_layer)

    def remove_layer(index):
        """ Removes map layer at given index """
        layer = self._layer_list.pop(index)
        layer._deactivate()

    def get_layer(self, index):
        """ Returns the layer at the given index """
        layer = self._layer_list[index]
        return layer


    ## Projection methods
    def getProjection(self):
        """ """
        return self._projection

    def setProjection(self, newProjection):
        """ """
        pass


    ## Location methods
    def set_POI(self, newPOI):
        """ Sets projection location of map  """
        self._POI = newPOI

    def get_POI(self):
        """ Returns the projection location """
        return self._POI

    def set_location(self, new_location):
        """ Sets geographic location on map """
        #! Add constaints
        self._POI = self.geo2proj(new_location)

    def get_location(self):
        """ Returns the geographic location on map """
        #! Add constaints
        return self.proj2geo(self._POI)

    def get_canvas_center(self):
        """ Returns a pixel point that is the center of the canvas. """
        x = int(self._size[0]/2)
        y = int(self._size[1]/2)
        return (x, y)


    ## Scale functions
    def set_scale(self, newScale):
        self._scale = newScale

    def get_scale(self):
        return self._scale


    ## Size methods
    def set_size(self, newSize): # size tuple (width, height)
        """ Sets size of  """
        self._size = newSize

    def get_size(self):
        """ """
        return self._size


    ## GeoFunctions Wrapper functions
    def geo2proj(self, geo_data):
        """
        """
        ## If dest_proj is WGS84, no convert is needed, pass geo_data to output
        if self._WGS84 == self._projection:
            return geo_data

        transformer = Transformer.from_proj(self._WGS84, self._projection)

        ## If geo_data is a list
        if isinstance(geo_data, list):

            lon = [coord[0] for coord in geo_data]
            lat = [coord[1] for coord in geo_data]

            lon = np.array(lon)
            lat = np.array(lat)

            #x, y = pyproj.transform(WGS84_proj, dest_proj, lat, lon)
            x, y = transformer.transform(lat, lon)

            proj_data = list( zip(x,y) )

        else:
            lon, lat = geo_data
            x, y = pyproj.transform(self._WGS84, self._projection, lat, lon) ## alwaysXy
            #x,y = y,x
            proj_data = (x, y)

        return proj_data

    def proj2geo(self, proj_data):
        """ """
        x, y = projPoint
        lon, lat = pyproj.transform(self._WGS84, self._projection, x, y)
        geo_data = (lat, lon)
        return geo_data


    def proj2pix(self, projPoint):
        """ """
        ## Unpack points
        focusX, focusY = self._POI
        centerX, centerY = self.get_canvas_center()

        ##
        if isinstance(projPoint, list):
            ## Break list of projPoints in x and y list
            x = [coord[0] for coord in projPoint]
            y = [coord[1] for coord in projPoint]

            ## Convert lists of points to numpy arrays
            x = np.array(x)
            y = np.array(y)

            #x = np.round(x, decimals=2)
            #y = np.round(y, decimals=2)

            ## Do math logic on all points
            pixelX = ((x - focusX) / self._scale) + centerX
            pixelY = -((y - focusY) / self._scale) + centerY

            ## Round to int to make drawing faster
            pixelX = np.rint(pixelX)
            pixelY = np.rint(pixelY)

            pixelX = pixelX[~np.isinf(pixelX)]
            pixelY = pixelY[~np.isinf(pixelY)]

            pixPoint = list( zip(pixelX, pixelY) )


        else:
            projX, projY = projPoint
            ##
            pixelX = ((projX - focusX) * self._scale) + centerX
            pixelY = -((projY - focusY) * self._scale) + centerY

            pixelX = int(pixelX)
            pixelY = int(pixelY)

            pixPoint = (pixelX, pixelY)

        return pixPoint

    def pix2proj(self, pixPoint):
        """ """
        ## Unpack points
        focusX, focusY = self._POI
        centerX, centerY = self.get_canvas_center()
        pixX, pixY = pixPoint

        ##
        projX = ((pixX - centerX) * self._scale) + focusX
        projY = ((pixY - centerY) * self._scale) + focusY

        ##
        projPoint = (projX, projY)


        ##
        return projPoint

    def geo2pix(self, geoPoint):
        """ """
        projPoint = self.geo2proj(geoPoint)
        pixPoint = self.proj2pix(projPoint)
        return pixPoint

    def pix2geo(self, pixPoint):
        """ """
        projPoint = self.pix2proj(pixPoint)
        geoPoint = self.proj2geo(projPoint)
        return geoPoint
