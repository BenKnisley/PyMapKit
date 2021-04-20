"""
Author: Ben Knisley [benknisley@gmail.com]
Date: 19 April, 2021
"""
import tempfile
import gdal
from .base_layer import BaseLayer


class RasterLayer(BaseLayer):
    def __init__(self, path):
        self.name = "Raster Layer"
        self.status = 'initializing'

        ## Open path with GDAL, if it fails raise exception
        self._gdal_raster = gdal.Open(path)
        if self._gdal_raster == None:
            raise Exception(f"{path}: Either doesn't exist, or isn't a valid raster file.")

        ## Set variables from args 
        self.path = path
        self.alpha = 1

        ##
        self.nodata_value = (0,0,0)

        ## Setup placeholder values
        self._img_path = None
        self._image_surface = None
        self._proj_x = None
        self._proj_y = None
        self._scale_x = None
        self._scale_y = None
        

    
    def activate(self):
        """ 
        Function called when layer is added to a Map Object.
        """
        ## Warp (transform) the original raster to parent maps srs into a tempfile  
        temp_tif = tempfile.NamedTemporaryFile(suffix='.tif', delete=False)

        ## GDAL Warp _gdal_raster parent projection into temp file
        '''
        if self.srcSRS:
            gdal.Warp(temp_tif.name, self._gdal_raster, srcSRS=self.srcSRS, dstSRS=self.parent.get_projection())
        else:
            gdal.Warp(temp_tif.name, self._gdal_raster, dstSRS=self.parent.get_projection())
        '''
        gdal.Warp(temp_tif.name, self._gdal_raster, dstSRS=self.map.projected_crs)

        ## Open the tempfile with GDAL and extract proj coords and scale
        temp_tiff = gdal.Open(temp_tif.name)
        self._proj_x, self._scale_x, _, self._proj_y, _, self._scale_y = temp_tiff.GetGeoTransform()

        ## Get Each color band
        R_band = temp_tiff.GetRasterBand(1)
        G_band = temp_tiff.GetRasterBand(2)
        B_band = temp_tiff.GetRasterBand(3)

        ## Set given nodata values
        R_band.SetNoDataValue(self.nodata_value[0])
        G_band.SetNoDataValue(self.nodata_value[1])
        B_band.SetNoDataValue(self.nodata_value[2])

        ## Save image data into temp png file
        temp_png = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        dst_driver = gdal.GetDriverByName('PNG')
        dst_driver.CreateCopy(temp_png.name, temp_tiff, 0, ["ZLEVEL=1"])

        ## Keep path of image data to cache during draw 
        self._img_path = temp_png.name
    
    def deactivate(self):
        ''' Method called by parent Map object when self is removed from it '''
        self._image_surface = None
        self._proj_x = None
        self._proj_y = None
        self._scale_x = None
        self._scale_y = None


    def __repr__(self):
        ''' What string should represent the layer '''
        return f"Raster Image from {self.path}"
    
    def get_extent(self):
        ''' Method that returns bounding box of all stored data'''
        pass
    
    def focus(self):
        ''' Method to move map to focus on layer '''
        pass
    
    def set_opacity(self):
        ''' Method to set opacity of whole layer '''
    
    def render(self, renderer, canvas):
        ''' Method '''
        if self._image_surface == None:
            self._image_surface = renderer.cache_image(self._img_path)

        pix_x, pix_y = self.map.proj2pix(self._proj_x, self._proj_y)

        scale_x = abs( self._scale_x / self.map._proj_scale )
        scale_y = abs( self._scale_y / self.map._proj_scale )
        
        renderer.draw_image(canvas, self._image_surface, pix_x, pix_y, scale_x, scale_y)