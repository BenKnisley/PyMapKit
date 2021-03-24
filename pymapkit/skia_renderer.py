"""
Project: PyMapKit
File: skia_renderer.py
Title: Skia Renderer Class
Function: Implements the drawing api using the PySkia library.
Author: Ben Knisley [benknisley@gmail.com]
Created: 5 February, 2021
"""
from .base_renderer import BaseRenderer
import skia

class SkiaRenderer(BaseRenderer):
    """
    Derived from the BaseRenderer abstract class, SkiaRenderer is an 
    implementation of the drawing API using the PySkia library.
    """

    def new_canvas(self, width, height):
        """
        Creates and returns a new Skia canvas.

        Creates a new Skia canvas ready for the SkiaRenderer instance to draw
        on. The new canvas is created via a new Skia surface. The new canvas is 
        returned, and the new surface is stored as `self.surface`. The new 
        surface has the width and height specified.

        Args:
            width (int): The width in pixels of the new Skia surface.
            height (int): The height in pixels of the new Skia surface.

        Returns:
            canvas (skia.Canvas): A new Skia canvas ready to be draw on.
        """
        self.surface = skia.Surface(width, height)
        canvas = self.surface.getCanvas()
        return canvas
    
    def is_canvas(self, target):
        """
        Returns whether a given item is a Skia canvas.

        Returns whether a given item is a Skia canvas and can be drawn on by 
        the renderer object.

        Args:
            target (*): The object to test.
        
        Returns:
            is_canvas (bool): Whether the test item is a skia canvas. 
        """
        return isinstance(target, skia.Canvas)
    
    def save(self, canvas, output):
        """
        Saves the rendered results to an output file.

        Saves the Skia surface to an output file. If output parameter is False 
        or None, then no file will be created. Currently only supports PNG 
        output. 

        Args:
            canvas (skia.Canvas): A Skia Canvas object.

            output (str): Path to output file.
        
        Returns:
            None
        """
        if output: ## For now, output is assumed to be in png format
            image = self.surface.makeImageSnapshot()
            image.save(output, skia.kPNG)

    ##
    ##
    ##

    def cache_color(self, input_color, opacity=1):
        """
        Saves the rendered results to an output file.

        Saves the Skia surface to an output file. If output parameter is False 
        or None, then no file will be created. Currently only supports PNG 
        output. 

        Args:
            input_color (string, tuple): A representation of a color. Valid 
             inputs include:
                - "Green"
                - 'black', opacity=0.4
                - #FFFFFF, opacity=0.9
                - (0.12, 0.39, 0.54)
                - (215, 0.39, 0.54), opacity=0.2

        Optional Args:
            opacity (float between 0 - 1): The opacity value of the color.
        
        Returns:
            cached_color (skia.Color): The skia Color value object for the 
             given color.
        """

        ## Valid input color formats


        if isinstance(input_color, str):
            ## Convert input_color string to lowercase
            input_color = input_color.lower()
            
            ## Convert color_name to hex color string
            if input_color in self.color_names:
                input_color = self.color_names[input_color]

            ## String should be a hex color at this point, so error out if not
            if input_color[0] != '#' or len(input_color) != 7:
                raise ValueError("Given color is invalid")
            
            ## Extract color values from hex string
            R = int(int(input_color[1:3], 16))
            G = int(int(input_color[3:5], 16))
            B = int(int(input_color[5:7], 16))
            A = int(opacity * 255)

            ## Convert to tuple
            input_color = (R, G, B, A)

        ## input_color mis required to be a tuple at this point
        if not isinstance(input_color, tuple):
            raise ValueError("Given color is invalid")
        
        ## Check if input tuple is in 1.0 max color format 
        if isinstance(max(input_color), float) and max(input_color) <= 1.0:
            R = int(input_color[0] * 255)
            G = int(input_color[1] * 255)
            B = int(input_color[2] * 255)
            A = int(opacity * 255)
            input_color = (R, G, B, A)

        ## If tuple has three values, add the alpha channel
        if len(input_color) == 3:
            R, G, B = input_color
            A = int(opacity * 255)
            input_color = (R, G, B, A)

        ## Return a skia.Color object
        return skia.Color(*input_color)





    ##
    ##
    ##
    

    def draw_background(self, canvas, color):
        pass
    
    ##
    ##
    ##

    def draw_point(self, canvas, structure, x_values, y_values, style):
        pass

    def draw_line(self, canvas, structure, x_values, y_values, style):
        pass

    def draw_polygon(self, canvas, structure, x_values, y_values, style):
        pass
    
    ##
    ##
    ##

    def cache_image(self, image_path):
        pass

    def draw_image(self, canvas, image_cache, x, y, x_scale, y_scale, align='nw'):
        pass
    
    ##
    ##
    ##

    def draw_text(self, canvas, text, text_style):
        pass