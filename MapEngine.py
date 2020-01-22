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
import numpy as np

## Import MapLayer and style
import MapEngine.GeoFunctions as GeoFunctions
import MapEngine.CairoMapPainter as CairoMapPainter


class MapEngine:
    """
    """
    def __init__(self, projection, initCoord):
        """ """
        ## Keep a reference WGS84
        self._WGS84 = pyproj.Proj("EPSG:4326")

        ## Variable projection
        self._proj = pyproj.Proj(projection)
        self._scale = 0.01
        self._POI = self.geo2proj(initCoord)

        ## Set default size
        self._size = (500, 500) ## Default to 500px x 500px

        ## Create MapPainter object
        self._map_painter = CairoMapPainter.CairoMapPainter()

        ## Create list to hold layers
        self._layer_list = []

    def addLayer(self, new_map_layer):
        """
        """
        self._layer_list.append(new_map_layer)


    def getProjection(self):
        return self._proj

    def setProjection(self, newProjection):
        None


    def setPOI(self, newPOI):
        """ """
        self._POI = newPOI

    def getPOI(self):
        return self._POI


    def zoomIn(self):
        self._scale -= (self._scale * 0.1)

    def zoomOut(self):
        self._scale += (self._scale * 0.1)


    def setScale(self, newScale):
        self._scale = newScale

    def getScale(self):
        return self._scale


    def setSize(self, newSize): # size tuple (x, y)
        self._size = newSize

    def getSize(self):
        return self._size


    def getCenterPoint(self):
        x = int(self._size[0]/2)
        y = int(self._size[1]/2)
        return (x, y)


    ## GeoFunctions Wrapper functions
    ## Added to

    def geo2proj(self, geo_data):
        """
        """
        proj_data = GeoFunctions.geo2proj(geo_data, self._WGS84, self._proj)
        return proj_data

    def proj2geo(self, proj_data):
        """ """
        geo_data = GeoFunctions.proj2geo(proj_data, self._WGS84, self._proj)
        return geo_data

    def proj2pix(self, projPoint):
        """ """
        ## Unpack points
        focusX, focusY = self._POI
        centerX, centerY = self.getCenterPoint()

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
        centerX, centerY = self.getCenterPoint()
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




    def paintCanvas(self, cr):
        """
        Draws map on canvas.
        Draws background, and calls draw on each layer.
        """
        ## Draw background
        cr.set_source_rgb(0.05, 0.05, 0.05) ## Set color to 95% black
        cr.rectangle( 0,0, self._size[0], self._size[1] ) ## Draw rectangle over entire widget
        cr.fill() ## Fill rectangle

        ## Draw each layer
        for layer in self._layer_list:
            layer.draw(cr)
