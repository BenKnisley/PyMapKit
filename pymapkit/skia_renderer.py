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
        pass
    
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