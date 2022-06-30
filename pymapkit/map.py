"""
Project: PyMapKit
File: map.py
Title: Map Class Definition
Function: Define the Map class that pymapkit project is build around.
Author: Ben Knisley [benknisley@gmail.com]
Created: 5 January, 2021
"""
import pyproj
import numpy as np
from typing import Union
from .base_style import Style
from .base_layer import BaseLayer
from .base_renderer import BaseRenderer


def get_renderer(renderer_name: str) -> BaseRenderer:
    """ 
    Returns a named renderer instance based on input string

    Args:
        renderer_name (str): The name of the renderer object to return.
    
    Returns:
        renderer (base_renderer): A renderer object of the type given with 
        renderer_name.
    """
    if renderer_name in ('skia', 'pyskia'):
        from .skia_renderer import SkiaRenderer
        renderer = SkiaRenderer()
    return renderer

class BackgroundStyle(Style):
    def __init__(self, parent_feature):
        Style.__init__(self, parent_feature)

        ## For map object, create a background domain
        background_domain = self.add_domain('background')

        ## Create a background none mode
        none_mode = background_domain.add_mode('none')

        ## Create a background color fill mode 
        color_mode = background_domain.add_mode('color')
        color_mode.add_property('color', 'white')
        color_mode.add_property('opacity', 1)

        ## Create a background color fill mode 
        image_mode = background_domain.add_mode('image')
        image_mode.add_property('path', None)
        image_mode.add_property('fit', 'full') ##

        ## Activate color fill mode
        background_domain.set_mode('color')

class Map:
    """
    Models a Map.

    A class that models a map. It has three primary functions:
        - Store and manage map data, such as: location, projections, and scale
        - Holds and manages map data layers
        - Serves as the entry point of the rendering pipeline, and controls 
            rendering
    """
    def __init__(self, renderer: Union[str, BaseRenderer]='pyskia') -> None:
        """
        Initializes a new Map object.

        Parameters:
            None

        Optional Parameters:
            - renderer (str | base_renderer obj): A string naming the renderer 
                to use, or a base_renderer instance to be used directly as the 
                renderer.
        
        Returns:
            None

        Exceptions:
            None
        """
        ## Create a list to hold layers
        self.layers: list[BaseLayer] = []

        ## Get the renderer
        if isinstance(renderer, str):
            self.renderer: BaseRenderer = get_renderer(renderer)
        else: 
            self.renderer: BaseRenderer = renderer
        
        ## Get the background style
        self.style: BackgroundStyle = BackgroundStyle(self)

        ## Create integers to hold width and height. Default 500x500
        self.width: int = 500
        self.height: int = 500

        ## Create a crs for input geographic points, & output projected points
        ## Default to WGS84 & Mercator
        self.geographic_crs: pyproj.crs.CRS = pyproj.crs.CRS("EPSG:4326")
        self.projected_crs: pyproj.crs.CRS = pyproj.crs.CRS("EPSG:3785")

        ## Create transformer objects
        self.transform_geo2proj = pyproj.Transformer.from_crs(
            self.geographic_crs, self.projected_crs, always_xy=True)
        self.transform_proj2geo = pyproj.Transformer.from_crs(
            self.projected_crs, self.geographic_crs, always_xy=True)

        ## Create a variable to hold scale
        self._proj_scale: float = 1.0 ## unit/pixel
        
        ## Set projection location
        self.proj_x: float = 0.0
        self.proj_y: float = 0.0

    def add(self, new_layer:BaseLayer, index:int=-1) -> None:
        """
        Adds a layer to the map.

        Parameters:
            - new_layer (BaseLayer): Layer to add to the map.

        Optional Parameters:
            - index (int): The index where to insert the new map layer.

        Returns:
            None
        
        Exceptions:
            - TypeError: raised when something other than a BaseLayer instance
                is provided as new_layer.

            - TypeError: raised when something other than an int is provided as 
                index.
        """
        ## Constrain new_layer type
        if not isinstance(new_layer, BaseLayer):
            type_str = type(new_layer).__name__
            error_msg = f"TypeError: Expected BaseLayer, {type_str} given."
            raise TypeError(error_msg)
        
        ## Constrain index type
        if not isinstance(index, int):
            type_str = type(index).__name__
            error_msg = f"TypeError: Expected int, {type_str} given."
            raise TypeError(error_msg)

        ## Call _activate on new_layer, a requirement for BaseLayer derivatives
        new_layer._activate(self)

        ## Add layer to layer list
        if index == -1:
            self.layers.append(new_layer)
        else:
            self.layers.insert(index, new_layer)

    def remove(self, del_layer:BaseLayer) -> None:
        """
        Removes a layer from the map.

        Parameters:
            - del_layer (BaseLayer): Layer to remove from the map.
        
        Returns:
            None
        
        Exceptions:
            - TypeError: raised when something other than a BaseLayer instance
                is provided as del_layer.

            - ValueError: raised when a layer not already in the map is provided
                as del_layer.
        """
        ## Constrain del_layer type
        if not isinstance(del_layer, BaseLayer):
            type_str = type(del_layer).__name__
            error_msg = f"TypeError: Expected BaseLayer, {type_str} given."
            raise TypeError(error_msg)

        ## Confirm layer currently exists in layer list
        if del_layer not in self.layers:
            error_msg = f"ValueError: Given layer not found"
            raise ValueError(error_msg)

        ## Call deactivate on del_layer
        del_layer._deactivate()

        ## Remove layer from layer list
        self.layers.remove(del_layer)

    def set_geographic_crs(self, new_crs:Union[str, pyproj.crs.CRS]):
        """
        Sets the base geographic reference system. 

        Sets the base geographic reference system, for accurate lat/lon to 
        projection conversion. Defaults to WGS84(EPSG:4326) 
        See: https://xkcd.com/2170/

        Parameters:
            - new_crs (str | pyproj.crs.CRS): The CRS to use as the base 
                geographic reference system.
        
        Returns:
            None
        
        Exceptions:
            - TypeError: If new_crs is not either a str or a pyproj.crs.CRS 
                object.
            
            - CRSError: If given projection is not a geographic projection.

            - CRSError: If given string is not a valid projection
        """
        ## Check input type of new_crs
        if isinstance(new_crs, pyproj.crs.CRS):
            ## If a CRS object is given directly
            new_geo_crs = new_crs
        elif isinstance(new_crs, str):
            ## If a string is given to represent the CRS
            new_geo_crs = pyproj.crs.CRS(new_crs)
        else:
            ## If any over input is given, raise type error
            raise TypeError(f'TypeError: Expected str or PyProj CRS object.')

        ## Check that new CRS is geographic
        if not new_geo_crs.is_geographic:
            msg = 'CRSError: Expected a geographic projection.'
            #@ Maybe make an in-house error for this?
            raise pyproj.exceptions.CRSError(msg) 

        ## Once projection is confirmed valid, set geographic_crs to new_geo_crs
        self.geographic_crs = new_geo_crs

        ## Recreate transformer objects
        self.transform_geo2proj = pyproj.Transformer.from_crs(
            self.geographic_crs, self.projected_crs, always_xy=True)
        self.transform_proj2geo = pyproj.Transformer.from_crs(
            self.projected_crs, self.geographic_crs, always_xy=True)

        ## Reactivate layers, to rebuild to new projection
        for layer in self.layers:
            layer.activate()

    def set_projection(self, new_crs:Union[str, pyproj.crs.CRS]):
        """
        Sets the projected coordinate system (projection) of the map.

        Sets the projected coordinate system of the map. Or how the map 
        displays the spherical coordinates on a 2D plane.

        Parameters:
            - new_crs (str | pyproj.crs.CRS): The CRS to use as the projected 
                reference system.
        
        Returns:
            None
        
        Exceptions:
            - TypeError: If new_crs is not either a str or a pyproj.crs.CRS 
                object.

            - CRSError: If given string is not a valid projection
        """
        ## Type check input
        if isinstance(new_crs, pyproj.crs.CRS):
            new_proj_crs = new_crs
        elif isinstance(new_crs, str):
            new_proj_crs = pyproj.crs.CRS(new_crs)
        else: ## If any over input is given, raise type error
            raise TypeError(f'TypeError: Expected str or PyProj CRS object.')

        ## Backup location and scale
        location = self.get_location()
        scale = self.get_scale()

        ## Once projection is confirmed valid: set projected_crs to new_proj_crs
        self.projected_crs = new_proj_crs
        
        ## Recreate transformer objects
        self.transform_geo2proj = pyproj.Transformer.from_crs(
            self.geographic_crs, self.projected_crs, always_xy=True)
        self.transform_proj2geo = pyproj.Transformer.from_crs(
            self.projected_crs, self.geographic_crs, always_xy=True)

        ## Reactivate layers, to rebuild to new projection
        for layer in self.layers:
            layer.activate()

        ## Restore location and scale
        self.set_location(*location)
        self.set_scale(scale)

    def set_location(self, latitude: float, longitude: float):
        """
        Sets the geographic location of the map.

        Sets the geographic location of the center of the map, location is 
        specified using lat/lon, and stored as projection x/y.

        Parameters:
            - latitude (float): The latitude coordinate of the map.
            
            - longitude (float): The longitude coordinate of the map.

        Returns:
            None

        Exceptions:
            None
        """
        geo_y, geo_x = latitude, longitude
        proj_x, proj_y = self.geo2proj(geo_x, geo_y)
        self.set_projection_coordinates(proj_x, proj_y)

    def get_location(self):
        """
        Returns the geographic location of the map.

        Returns the geographic location of the center of the map, location is
        returned in lat/lon.

        Parameters:
            None

        Returns:
            - latitude (float): The latitude coordinate of the map.
            
            - longitude (float): The longitude coordinate of the map.

        Exceptions:
            None
        """
        geo_x, geo_y = self.proj2geo(self.proj_x, self.proj_y)
        latitude, longitude = geo_y, geo_x
        return latitude, longitude

    def set_projection_coordinates(self, new_x: float, new_y: float):
        """
        Directly sets the projected location of the map.
        
        Parameters:
            - new_x (float): The x value of the projections coordinate of the map
                location.
            
            - new_y (float): The y value of the projections coordinate of the map
                location.

        Returns:
            None
        
        Exceptions:
            - TypeError: raised when something other than a number is given as 
                input.
        """
        ## Type check inputs
        if not isinstance(new_x, (float, int)):
            type_str = type(new_x).__name__
            msg = f'TypeError: Expected float, {type_str} given.'
            raise TypeError(msg)
        
        if not isinstance(new_y, (float, int)):
            type_str = type(new_y).__name__
            msg = f'TypeError: Expected float, {type_str} given.'
            raise TypeError(msg)

        ## Set projection coord values
        self.proj_x = new_x
        self.proj_y = new_y

    def get_projection_coordinates(self):
        """
        Returns the projected location of the map.

        Returns the projected location of the center of the map, location is 
        returned as x, y.

        Args:
            None

        Returns:
            x (float): The x value of the projections coordinate of the map
            location.
            y (float): The y value of the projections coordinate of the map
            location.
        """
        return self.proj_x, self.proj_y

    def set_scale(self, new_scale, proj_units=False):
        """
        Set the scale of the map.

        Sets the scale of the map. Scale is in m/pix, independent of the map 
        projections' base unit. Unless the optional `proj_units` flag is set to
        true, then the new scale is set to use the map's projections units/pix.

        Args:
            new_scale (float): The new scale of the map in meters per pixel.

        Optional Args:
            proj_units (bool): Whether to use the map's projections unit/pix 
            instead of m/pix. Defaults to false. 

        Returns:
            None
        """

        if proj_units:
            self._proj_scale = float(new_scale)
            return

        ## Get unit code of base unit of projection
        proj_unit = self.projected_crs.axis_info[0].unit_code

        if proj_unit == '9003': ## 9003 == US survey foot
            ## Meters to feet
            new_scale = new_scale * 3.28084

        if proj_unit == '9122': ## 9122 == degree':
            ## degrees to meters
            new_scale = new_scale / 110570

        #@ NOTE: Add more units

        ## Set scale in proj units per pix
        self._proj_scale = float(new_scale)

    def get_scale(self):
        """
        Returns the map scale in meters per pixel.

        Returns the scale of the map in meters per pixel. Scale is always in 
        m/pix and thus is independent of the projections' base unit. This is 
        done by converting internal projection scale to the m/pix scale.

        Args:
            None

        Returns:
            scale (float): The scale of the map in meters per pixel.
        """
        ## Get current scale in units/pix
        proj_scale = self._proj_scale

        ## Get unit code of base unit of projection
        proj_unit = self.projected_crs.axis_info[0].unit_code

        if proj_unit == '9001':
            return proj_scale

        if proj_unit == '9003': ## 9003 == US survey foot
            ## Meters to feet
            return proj_scale / 3.28084

        if proj_unit == '9122': ## 9122 == degree':
            ## meters to degrees
            return proj_scale * 110570

    def set_size(self, width, height):
        """
        Sets the pixel size of the canvas.

        Sets the pixel width & height of the map area.

        Arguments:
            - width (int): the new width of the map canvas.
            - height (int): the new width of the map canvas.

        Returns: None
        """

        self.width = width
        self.height = height

    def get_size(self):
        """
        Returns the pixel size on the map canvas.

        Returns the width & height of the map area.

        Args:
            width (int): The width of the map canvas in pixels.
            height (int): The height of the map canvas in pixels.
            
        Returns:
            None
        """
        return self.width, self.height

    def zoom_in(self, factor=1.5):
        """
        Zooms the map in by shrinking the map scale.

        Changes the map scale by dividing by a factor (1.5 default).

        Args:
            None

        Optional Args:
            factor (int | float): The scaling factor to divide by.

        Returns:
            None
        """
        self.set_scale(self.get_scale()/factor)

    def zoom_out(self, factor=1.5):
        """
        Zooms the map out by increasing the map scale.

        Changes the map scale by multiplying by a factor (1.5 default).

        Args:
            None

        Optional Args:
            factor (int | float): The scaling factor to multiplying by.

        Returns:
            None
        """
        self.set_scale(self.get_scale() * factor)

    def set_renderer(self, renderer):
        """
        Tells the map which renderer to use to render the map.

        Sets the renderer to be used to render the map data. Set from a string 
        or a directly given renderer object.

        Args:
            renderer (str | base_renderer obj): A string naming the renderer to
            use, retrieved via the get_renderer function. Or a base_renderer 
            object to be used directly as the renderer.
            
        Returns:
            None
        """

        if isinstance(renderer, str):
            self.renderer = get_renderer(renderer)
        else: 
            self.renderer = renderer

    def render(self, output=None, *args):
        """
        Renders the map.
        
        Renders all map data stored in map layers to a map canvas with a map 
        renderer.

        Args:
            None
        
        Optional Args:
            output (str): The location to store the output map. Defaults to 
            None, meaning the map will be drawn, but not be saved.

            args (tuple): All other arguments will be sent to the 
            renderer.save method if called.

        Returns:
            None
         
        """

        output_file = None
        
        if self.renderer.is_canvas(output):
            output_file = output
            canvas = self.renderer
        else:
           canvas = self.renderer.new_canvas(self.width, self.height)
           output_file = output
        
        ## Draw background
        self.renderer.draw_background(canvas, self.style)

        ## Draw each layer, pass renderer, and canvas to each object
        for layer in self.layers:
            layer.render(self.renderer, canvas)
        
        ## Save or display canvas
        self.renderer.save(canvas, output_file)

    def geo2proj(self, geo_x, geo_y):
        """
        Converts geographic coordinates to projection coordinates.

        Converts geographic coordinates, either singlet or vectorized, to 
        projection coordinates of the maps CRS. Output is same type as input.

        Args:
            geo_x (int | float | list): The input longitude or geographic x 
            value(s) to convert.

            geo_y (int | float | list): The input latitude or geographic y 
            value(s) to convert.
    

        Returns:
            proj_x (int | float | list): The output x value(s).

            proj_y (int | float | list): The output y value(s).
        """
        ## Use geo2proj transform to convert points
        proj_x, proj_y = self.transform_geo2proj.transform(geo_x, geo_y)
        return proj_x, proj_y
    
    def proj2geo(self, proj_x, proj_y):
        """
        Converts projection coordinates to geographic coordinates.

        Converts projection coordinates using the maps CRS, either singlet or 
        vectorized, to geographic coordinates. Output is same type as input.

        Args:
            proj_x (int | float | list): The input projected x value(s) to 
            convert.

            proj_y (int | float | list): The input projected y value(s) to 
            convert.
    

        Returns:
            geo_x (int | float | list): The output longitude (x) value(s).

            geo_y (int | float | list): The output latitude (y) value(s).
        """
        geo_x, geo_y = self.transform_proj2geo.transform(proj_x, proj_y)
        return geo_x, geo_y

    def proj2pix(self, proj_x, proj_y):
        """
        Converts projection coordinates to canvas pixel coordinates.

        Converts projection coordinates using the maps CRS, either singlet or 
        vectorized, to canvas pixel coordinates with (0,0) at the top left 
        corner of the map. Output type is same type as input.

        Args:
            proj_x (int | float | list): The input projected x value(s) to 
            convert.

            proj_y (int | float | list): The input projected y value(s) to 
            convert.
    

        Returns:
            canvas_x (int | float | list): The output pixel x value(s).

            canvas_y (int | float | list): The output pixel y value(s).
        """
        ## Flag true if input is list
        list_flag = False

        ## Convert list to numpy array
        if isinstance(proj_x, list):
            list_flag = True
            proj_x = np.array(proj_x)
            proj_y = np.array(proj_y)
        
        ## Do math logic on all points
        # NOTE: @ self._proj_scale has to be a float!
        pix_x = ((proj_x - self.proj_x) / self._proj_scale) + int(self.width / 2)
        pix_y = -((proj_y - self.proj_y) / self._proj_scale) + int(self.height / 2)

        ## Convert numpy array to list
        if list_flag:
            pix_x = pix_x.tolist()
            pix_y = pix_y.tolist()
        
        return pix_x, pix_y

    def pix2proj(self, pix_x, pix_y):
        """
        Converts canvas pixel coordinates to projection coordinates.

        Converts canvas pixel coordinates to projection coordinates with the 
        maps CRS. Input can be either singlet or vectorized. Canvas coordinates 
        origin (0,0) is at the top left corner of the map. Output type is same 
        as input type.

        Args:
            pix_x (int | float | list): The input canvas x value(s) to 
            convert.

            pix_y (int | float | list): The input canvas y value(s) to 
            convert.
    
        Returns:
            proj_x (int | float | list): The output projection x value(s).

            proj_y (int | float | list): The output projection y value(s).
        """
        ## Flag true if input is list
        list_flag = False

        ## Convert list to numpy array
        if isinstance(pix_x, list):
            pix_x = np.array(pix_x)
            pix_y = np.array(pix_y)
            list_flag = True
        
        ## Do math logic on all points
        #! NOTE: @ self._proj_scale has to be a float!
        #! NOTE: a round(...) might be better 
        proj_x = self.proj_x + ((pix_x - int(self.width / 2)) * self._proj_scale) 
        proj_y = (self.proj_y + ((pix_y - int(self.height / 2)) * self._proj_scale))


        ## Convert numpy array to list
        if list_flag:
            proj_x = proj_x.tolist()
            proj_y = proj_y.tolist()
        
        return proj_x, proj_y

    def geo2pix(self, geo_x, geo_y):
        """
        Converts geographic coordinates to canvas pixel coordinates.

        Converts geographic coordinates directly to canvas pixel coordinates.
        Input can be either singlet or vectorized. Output will be same type as 
        input. Canvas pixel coordinates are set to have (0,0) at the top left 
        corner of the map.

        Args:
            geo_x (int | float | list): The input longitude or geographic x 
            value(s) to convert.

            geo_y (int | float | list): The input latitude or geographic y 
            value(s) to convert.

        Returns:
            canvas_x (int | float | list): The output pixel x value(s).

            canvas_y (int | float | list): The output pixel y value(s).
        """
        proj_x, proj_y = self.geo2proj(geo_x, geo_y)
        canvas_x, canvas_y = self.proj2pix(proj_x, proj_y)
        return canvas_x, canvas_y
    
    def pix2geo(self, pix_x, pix_y):
        """
        Converts canvas pixel coordinates to geographic coordinates.

        Converts canvas pixel coordinates to geographic coordinates.
        Input can be either singlet or vectorized.
        Canvas pixel coordinates have (0,0) at the top left corner of the map.
        Output type is same type as input.

        Args:
            pix_x (int | float | list): The input canvas x value(s) to 
            convert.

            pix_y (int | float | list): The input canvas y value(s) to 
            convert.

        Returns:
            geo_x (int | float | list): The output longitude (x) value(s).

            geo_y (int | float | list): The output latitude (y) value(s).
        """
        proj_x, proj_y = self.pix2proj(pix_x, pix_y)
        geo_x, geo_y = self.proj2geo(proj_x, proj_y)
        return geo_x, geo_y