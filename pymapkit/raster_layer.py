"""
Author: Ben Knisley [benknisley@gmail.com]
Date: 19 April, 2021
"""
import os
import tempfile
import gdal
import pyproj
from .base_layer import BaseLayer


class RasterLayer(BaseLayer):
    """
    A class providing a single raster image as a map layer.
    """

    def __init__(self, path):
        """
        RasterLayer Class Constructor

        Initializes a raster layer from a given path.

        Args:
            path (str): The path of the file containing the raster.
        
        Returns:
            None
        """
        ## Implement BaseLayer
        BaseLayer.__init__(self)

        ## Update layer status & name
        self.status = 'initializing'
        self.name = "Raster Layer"
        
        ## Open given path with GDAL, if loading fails raise exception
        self.gdal_raster = gdal.Open(path)
        if self.gdal_raster == None:
            raise Exception(f"{path}: file either doesn't exist, or isn't a valid raster file.")

        ## Store path of original raster data, & update name
        self.path = path
        self.name = os.path.basename(path)
        
        ## Set up mutable RGB for raster nodata value
        self.nodata_value = (0,0,0)

        ## Init alpha value
        self.alpha = 1

        ## Setup location and placement variables
        self.proj_x = None
        self.proj_y = None
        self.scale_x = None
        self.scale_y = None

        ## Setup image storage variables
        self.image_path = None
        self.image_cache = None
        
        ## Update Status
        self.status = 'initialized'

    def __repr__(self):
        """
        Returns string representation of layer.
        """
        return f"Raster Layer: {self.name} ({self.path})"

    def activate(self):
        """
        Activates the layer after the layer is added to a map object.

        Reprojects raster image to the parent maps; projection, and copies 
        image data into a temporary png file with nodata values transparent.

        Args:
            None
        
        Returns:
            None
        """
        ## Update Status
        self.status = 'loading'
        
        ## Create a temp raster file to store reprojected raster
        temp_tif = tempfile.NamedTemporaryFile(suffix='.tif', delete=False)

        ## Reproject & load gdal raster into temp raster file
        gdal.Warp(temp_tif.name, self.gdal_raster, dstSRS=self.map.projected_crs)

        ## Open the temp raster with GDAL and extract proj coords and scale
        temp_tiff = gdal.Open(temp_tif.name)
        self.proj_x, self.scale_x, _, self.proj_y, _, self.scale_y = temp_tiff.GetGeoTransform()

        ## Set nodata values for each band, so it is transparent in png file
        R_band = temp_tiff.GetRasterBand(1)
        G_band = temp_tiff.GetRasterBand(2)
        B_band = temp_tiff.GetRasterBand(3)
        R_band.SetNoDataValue(self.nodata_value[0])
        G_band.SetNoDataValue(self.nodata_value[1])
        B_band.SetNoDataValue(self.nodata_value[2])

        ## Use GDAL to save image data into temp png file
        png_driver = gdal.GetDriverByName('PNG')
        temp_png = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        png_driver.CreateCopy(temp_png.name, temp_tiff, 0, ["ZLEVEL=1"])

        ## Save temp_png path as image_path
        self.image_path = temp_png.name

        ## Update layer status
        self.status = 'ready'

    def deactivate(self):
        """
        Deactivates layer, making layer available to add to a new map object.

        Args:
            None
        
        Returns:
            None
        """
        self.status = 'deactivating'
        self.image_cache = None
        self.proj_x = None
        self.proj_y = None
        self.scale_x = None
        self.scale_y = None
        self.status = 'initialized'

    def get_extent(self):
        """
        Returns the extent of the raster data, using the map projections 
        coordinates system.

        Args:
            None

        Returns:
            geo_x_min (float): The min x value of the data
            geo_y_min (float): The min y value of the data
            geo_x_max (float): The max x value of the data
            geo_y_max (float): The max y value of the data
        """
        ##
        raster_x_min, x_fact, _, raster_y_min, _, y_fact = self.gdal_raster.GetGeoTransform()

        ##
        raster_x_max = raster_x_min + (self.gdal_raster.RasterXSize * x_fact)
        raster_y_max = raster_y_min + (self.gdal_raster.RasterYSize * y_fact)

        ##
        raster_crs = pyproj.crs.CRS(self.gdal_raster.GetProjection())

        ##
        proj_x_vals, proj_y_vals = pyproj.transform(
            raster_crs, self.map.projected_crs, 
            (raster_x_min, raster_x_max), (raster_y_min, raster_y_max),
            always_xy=True
        )
        
        ## Unpack 
        proj_x_min, proj_x_max = proj_x_vals
        proj_y_min, proj_y_max = proj_y_vals

        return proj_x_min, proj_y_min, proj_x_max, proj_y_max
    
    def clear_cache(self):
        """
        Clears cached image.

        Args:
            None
        
        Returns:
            None
        """
        self.image_cache = None

    def render(self, renderer, canvas):
        """
        Renders the data onto the given canvas, using the given renderer.

        Args:
            renderer (BaseRenderer): The renderer object to use the render the
            data.

            canvas (BaseCanvas): The canvas object to render the data onto.
        
        Returns:
            None
        """
        ## Update Status
        self.status = 'rendering'

        ## Cache image if required
        if self.image_cache == None:
            self.image_cache = renderer.cache_image(self.image_path)

        ## Get pixel location
        pix_x, pix_y = self.map.proj2pix(self.proj_x, self.proj_y)

        ## Calculate scale 
        scale_x = abs( self.scale_x / self.map._proj_scale )
        scale_y = abs( self.scale_y / self.map._proj_scale )
        
        ## Draw image onto canvas
        renderer.draw_image(canvas, self.image_cache, pix_x, pix_y, scale_x, scale_y, opacity=self.alpha)

        ## Update Status
        self.status = 'ready'