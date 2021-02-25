"""
Author: Ben Knisley [benknisley@gmail.com]
Date:
"""
from .base_renderer import BaseRenderer
import skia

class SkiaRenderer(BaseRenderer):
    """
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
        pass
    
    def save(self, canvas, output):
        pass

    ##
    ##
    ##

    def cache_color(self, color):
        pass

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