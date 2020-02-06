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
    def draw_map(self, cr):
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

        ## Set RGB values from color parser function
        self._background_color = self._map_painter.color_converter(input_color)

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
    def get_projection(self):
        """ """
        return self._projection

    def set_projection(self, new_projection):
        """ """
        if isinstance(new_projection, str):
            self._projection = pyproj.Proj(new_projection)

        else: ## PyProj object TODO: Check that it is PyProj object
            self._projection = new_projection



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
