"""
Project: PyMapKit
Title: Raster Data Layer
Function: Provides a class that can display raster based geospatial data.
Author: Ben Knisley [benknisley@gmail.com]
Created: 8 February, 2020
"""
import gdal
import tempfile
 
class RasterLayer:
    """ """
    def __init__(self, path, clear_nodata=False, nodata_value=(0,0,0), projection=None):
        """ """
        ## Open path with GDAL, if it fails raise exception
        self._gdal_raster = gdal.Open(path)
        if self._gdal_raster == None:
            raise Exception(f"{path}: Either doesn't exist, or isn't a valid raster file.")

        ## Set variables from args 
        self.path = path

        ## Create a name property
        self.name = "RasterLayer"

        #$ clear_nodata flag says whether to make nodata pixels transparent 
        self.clear_nodata = clear_nodata
        self.srcSRS = projection
        self.nodata_value = nodata_value

        self.parent = None
        self.alpha = 1

        ## Setup placeholder values
        self._img_path = None
        self._image_surface = None
        self._proj_x = None
        self._proj_y = None
        self._scale_x = None
        self._scale_y = None

    def _activate(self, new_parent_map):
        """ Function called when layer is added to a Map Object."""
        self.parent = new_parent_map

        ## Warp (transform) the original raster to parent maps srs into a tempfile  
        temp_tif = tempfile.NamedTemporaryFile(suffix='.tif', delete=False)

        if self.srcSRS:
            gdal.Warp(temp_tif.name, self._gdal_raster, srcSRS=self.srcSRS, dstSRS=self.parent.get_projection())
        else:
            gdal.Warp(temp_tif.name, self._gdal_raster, dstSRS=self.parent.get_projection())


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

        temp_png = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        dst_driver = gdal.GetDriverByName('PNG')
        dst_ds = dst_driver.CreateCopy(temp_png.name, temp_tiff)
        
        ## Keep path of image data to cache during draw 
        self._img_path = temp_png.name

    def _deactivate(self):
        """ Function called when layer is removed from a Map object"""
        self.parent = None
        self._image_surface = None
        self._proj_x = None
        self._proj_y = None
        self._scale_x = None
        self._scale_y = None

    #! Rename to set opacity
    def set_transparency(self, new_transparency):
        """
        """
        self.alpha = new_transparency
    
    def focus(self):
        """
        """
        pass

    def draw(self, renderer, cr):
        """ """
        if self._image_surface == None:
            self._image_surface = renderer.cache_image(self._img_path)

        pix_x, pix_y = self.parent.proj2pix(self._proj_x, self._proj_y)

        scale_x = abs( self._scale_x / self.parent._scale )
        scale_y = abs( self._scale_y / self.parent._scale )
        
        renderer.draw_image(cr, self._image_surface, pix_x, pix_y, scale_x, scale_y)


