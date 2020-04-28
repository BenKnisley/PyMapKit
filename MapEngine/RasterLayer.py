#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date: Febuary 8, 2020
"""
import os
from osgeo import ogr
import numpy as np
import gdal
import pyproj
import tempfile
import cairo
from PIL import Image

class RasterLayer:
    """ """
    def __init__(self, path):
        """ """
        ## Init MapEngine object
        self._MapEngine = None

        ## open raster with gdal
        self.gdal_raster = gdal.Open(path)

        ## Extract projection, scale, and location from raster
        self._init_proj = pyproj.Proj(self.gdal_raster.GetProjection())

        ##
        self._init_proj_x, self._init_scale_x, _, self._init_proj_y, _, self._init_scale_y = self.gdal_raster.GetGeoTransform()

    
    def _activate(self, new_MapEngine):
        """ Function called when layer is added to a MapEngine layer list."""
        self._MapEngine = new_MapEngine

        ## Create a tempfile geotif file
        temp_tif = tempfile.NamedTemporaryFile(suffix='.tif', delete=False)			      
	      
        ## Reproject to mapengines projection into temp_tif 
        gdal.Warp(temp_tif.name, self.gdal_raster, dstSRS=self._MapEngine.get_projection())


        ## Create a temp PNG 
        ## Load/convert temp_tif into temp_png
        temp_png = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        
        #Image.MAX_IMAGE_PIXELS = 9331200000000
        im = Image.open(temp_tif.name)
        
        im = im.convert("RGBA")
        datas = im.getdata()

        ## Convert pure black pixels to transpancy 
        newData = []
        for item in datas:
            if item[0] == 0 and item[1] == 0 and item[2] == 0:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)

        im.putdata(newData)
        
        im.save(temp_png.name, "PNG")
        



        self.image_surface = cairo.ImageSurface.create_from_png(temp_png.name)

        ## 
        self._proj_x, self._proj_y =  pyproj.transform(self._init_proj, self._MapEngine.get_projection(), self._init_proj_x, self._init_proj_y)


    def _deactivate(self):
        """ Function called when layer is added to a MapEngine """
        pass


    def draw(self, renderer, cr):
        """ """
        pix_x, pix_y = self._MapEngine.proj2pix(self._proj_x, self._proj_y)

        cr.save()
        
        scale_fact_x = abs( self._init_scale_x / self._MapEngine._scale )
        scale_fact_y = abs( self._init_scale_y / self._MapEngine._scale )
        
        cr.translate(pix_x, pix_y)
        cr.scale(scale_fact_x, scale_fact_y)

        cr.set_source_surface(self.image_surface)

        cr.paint()
        cr.restore()



