#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date: February 8, 2020
"""
import gdal
import tempfile
import cairo
from PIL import Image
 
class RasterLayer:
    """ """
    def __init__(self, path, clear_nodata=True):
        """ """
        ## Open path with GDAL, if it fails raise exception
        self._gdal_raster = gdal.Open(path)
        if self._gdal_raster == None:
            raise Exception(f"{path}: Either doesn't exist, or isn't a valid raster file.")

        ## Set variables from args 
        self.path = path

        #$ clear_nodata flag says whether to make nodata pixels transparent 
        self.clear_nodata = clear_nodata

        ## Setup placeholder values
        self._MapEngine = None
        self._image_surface = None
        self._proj_x = None
        self._proj_y = None
        self._scale_x = None
        self._scale_y = None

    def _activate(self, new_MapEngine):
        """ Function called when layer is added to a MapEngine layer list."""
        ## Update MapEngine 
        self._MapEngine = new_MapEngine

        ## Warp (transform) the original raster to new_MapEngine srs into a tempfile  
        temp_tif = tempfile.NamedTemporaryFile(suffix='.tif', delete=False)
        gdal.Warp(temp_tif.name, self._gdal_raster, dstSRS=self._MapEngine.get_projection())

        ## Open the tempfile with GDAL and extract proj coords and scale
        temp_tiff = gdal.Open(temp_tif.name)
        self._proj_x, self._scale_x, _, self._proj_y, _, self._scale_y = temp_tiff.GetGeoTransform()

        #Image.MAX_IMAGE_PIXELS = 9331200000000
        
        ## Load image data with PIL
        image = Image.open(temp_tif.name)

        ## If clear_nodata flag is set, make nodata pixels transparent
        if self.clear_nodata:
            ## Convert to RGBA colorspace, and get image_data
            image = image.convert("RGBA")
            image_data = image.getdata()
            
            ## Loop through all pixels: loading them into new_image_data
            new_image_data = []
            for pixel in image_data:
                if pixel[0] == 0 and pixel[1] == 0 and pixel[2] == 0:
                    new_image_data.append( (255, 255, 255, 0) )
                else:
                    new_image_data.append(pixel)

            ## Put manipulated data into image
            image.putdata(new_image_data)
        
        ## Save image data into a tempfile, converting into PNG
        temp_png = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        image.save(temp_png.name, "PNG")
        
        ## Cache image data
        self._image_surface = cairo.ImageSurface.create_from_png(temp_png.name)

    def _deactivate(self):
        """ Function called when layer is added to a MapEngine """
        pass

    def draw(self, renderer, cr):
        """ """
        pix_x, pix_y = self._MapEngine.proj2pix(self._proj_x, self._proj_y)

        cr.save()
        
        scale_fact_x = abs( self._scale_x / self._MapEngine._scale )
        scale_fact_y = abs( self._scale_y / self._MapEngine._scale )
        
        cr.translate(pix_x, pix_y)
        cr.scale(scale_fact_x, scale_fact_y)

        cr.set_source_surface(self._image_surface)

        cr.paint()
        cr.restore()



