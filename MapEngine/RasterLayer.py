#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date: Febuary 8, 2020
"""
from osgeo import ogr
import numpy as np

class RasterLayer:
    """ """
    def __init__(self):
        """ """
        self._MapEngine = None

    def _activate(self, new_MapEngine):
        """ Function called when layer is added to a MapEngine layer list."""
        self._MapEngine = new_MapEngine

    def _deactivate(self):
        """ Function called when layer is added to a MapEngine """
        pass

    def draw(self, renderer, cr):
        """ """
        pix_x, pix_y = self._MapEngine.geo2pix(-83.0, 40.0)
        cr.rectangle(pix_x, pix_y, 50, 50)
        cr.set_source_rgb(1,1,1)
        cr.fill()



def from_geotiff(path):
    return RasterLayer()