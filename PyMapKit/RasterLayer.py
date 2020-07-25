"""
Project: PyMapKit
Title: Raster Data Layer
Function: Provides a class that can display raster based geospatial data.
Author: Ben Knisley [benknisley@gmail.com]
Created: 8 February, 2020
"""
import gdal
import tempfile
from PIL import Image
 
class RasterLayer:
    """ """
    def __init__(self, path, clear_nodata=False):
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
        gdal.Warp(temp_tif.name, self._gdal_raster, dstSRS=self.parent.get_projection())

        ## Open the tempfile with GDAL and extract proj coords and scale
        temp_tiff = gdal.Open(temp_tif.name)
        self._proj_x, self._scale_x, _, self._proj_y, _, self._scale_y = temp_tiff.GetGeoTransform()

        #image.MAX_IMAGE_PIXELS = 9331200000000
        
        ## Load image data with PIL
        image = Image.open(temp_tif.name)

        ## If clear_nodata flag is set, make nodata pixels transparent
        if self.clear_nodata:
            ## Convert to RGBA colorspace
            image = image.convert("RGBA")
            
            ## Loop through all pixels: loading them into new_image_data
            new_image_data = []
            for pixel in image.getdata():
                if pixel == (0,0,0,255):
                    pixel = (0, 0, 0, 0)
                new_image_data.append(pixel)
            
            ## Put updated image data into image 
            image.putdata(new_image_data)
        
        ## Save image into a tempfile, converting into PNG
        temp_png = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        image.save(temp_png.name, "PNG")
        
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
            self._image_surface = renderer.get_image_obj(self._img_path)

        pix_x, pix_y = self.parent.proj2pix(self._proj_x, self._proj_y)

        scale_x = abs( self._scale_x / self.parent._scale )
        scale_y = abs( self._scale_y / self.parent._scale )
        
        renderer.draw_image(cr, self._image_surface, pix_x, pix_y, scale_x, scale_y)


