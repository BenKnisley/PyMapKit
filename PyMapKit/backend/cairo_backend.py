"""
Project: PyMapKit
Title: Cairo Rendering Backend
Function: Define CairoBackend class and contain all cairo drawing functionality.
Author: Ben Knisley [benknisley@gmail.com]
Created: 1 January, 2020
"""
from .base_backend import BaseBackend
import numpy as np
import cairo

class CairoBackend(BaseBackend):
    def new_canvas(self, width, height):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        canvas = cairo.Context(self.surface)
        return canvas
    
    def is_canvas(self, target):
        return isinstance(target, cairo.Context)
    
    def save(self, canvas, output):
        if output:
            self.surface.write_to_png(output)

    def cache_image(self, image_path):
        return cairo.ImageSurface.create_from_png(image_path)

    def cache_color(self, input_color, opacity=1):
        ## Two tuple types, 0-1 or 0-256
        if isinstance(input_color, tuple):
            if isinstance(input_color[0], float):
                rtrn_color = *input_color, opacity
                return rtrn_color

            elif isinstance(input_color[0], int):
                R = input_color[3] / 255.0
                G = input_color[5] / 255.0
                B = input_color[7] / 255.0
                return (R,G,B, opacity)

        ## Two types of color strings: Html color names and hex
        if isinstance(input_color, str):
            ##
            if input_color.lower() in BaseBackend.color_names:
                input_color = BaseBackend.color_names[input_color.lower()]

            if '#' in input_color and len(input_color) == 7:
                ## Hex string color
                R = int(input_color[1:3], 16) / 255.0
                G = int(input_color[3:5], 16) / 255.0
                B = int(input_color[5:7], 16) / 255.0
                return (R,G,B, opacity)


    def draw_background(self, canvas, *color): #? Make sure background can be transparent
        canvas.set_source_rgba(*self.cache_color(*color))
        canvas.paint()

    def draw_point(self, canvas, structure, x_values, y_values, style):
        ## Cache colors
        if not style.cached_renderer:
            style.cache_renderer(self)
        elif style.cached_renderer != self:
            style.cache_renderer(self)
        
        ## Draw point
        pointer = 0
        for p_count in structure:
            for index in range(pointer, pointer+p_count):
                ## Draw outline
                canvas.set_source_rgba(*style._outline_color_cache)
                canvas.arc(x_values[index], y_values[index], style.weight+style.outline_weight, 0, 6.2830)
                canvas.fill()

                ## Draw body
                canvas.set_source_rgba(*style._color_cache)
                canvas.arc(x_values[index], y_values[index], style.weight, 0, 6.2830)
                canvas.fill()
            pointer += p_count

    def draw_line(self, canvas, structure, x_values, y_values, style):
        ## Cache colors
        if not style.cached_renderer:
            style.cache_renderer(self)
        elif style.cached_renderer != self:
            style.cache_renderer(self)

        canvas.set_source_rgba(*style._outline_color_cache)
        canvas.set_line_width(style.weight+style.outline_weight)

        pointer = 0
        for p_count in structure:
            canvas.move_to( x_values[pointer], y_values[pointer] )
            for index in range(pointer, pointer+p_count):
                canvas.line_to( x_values[index], y_values[index] )
            
            ## Color in outline
            canvas.stroke_preserve()
            
            ## Color in line
            canvas.set_line_width(style.weight)
            canvas.set_source_rgba(*style._color_cache)
            canvas.stroke()

        pointer += p_count
    
    def draw_polygon(self, canvas, structure, x_values, y_values, style):
        ## Cache colors
        if not style.cached_renderer:
            style.cache_renderer(self)
        elif style.cached_renderer != self:
            style.cache_renderer(self)

        ## Draw polygon
        pointer = 0
        for p_count in structure:
            canvas.move_to( x_values[pointer], y_values[pointer] )

            for index in range(pointer, pointer+p_count):
                canvas.line_to(x_values[index], y_values[index])
            pointer = pointer + p_count

        canvas.set_source_rgba(*style._color_cache)
        canvas.fill_preserve()

        canvas.set_source_rgba(*style._outline_color_cache)
        canvas.set_line_width(style.outline_weight)
        canvas.stroke()


    def draw_image(self, canvas, image_cache, x, y, x_scale, y_scale, align='nw'):
        #def draw_image(self, cr, img_surface, pix_x, pix_y, scale_x, scale_y):
        if align != 'nw':
            if align[0] == 'c': ## Center
                x -= int((image_cache.get_width() * x_scale) / 2.0)
                y -= int((image_cache.get_height() * y_scale) / 2.0)
            else:
                pass #! ADD MORE

        canvas.save()
        canvas.translate(x, y)
        canvas.scale(x_scale, y_scale)
        canvas.set_source_surface(image_cache, 0, 0)
        canvas.paint()
        canvas.restore()
    
    def draw_text(self, canvas, text_line, x_pos, y_pos, text_style=None):
        """ """
        if text_line.italic:
            slant = cairo.FONT_SLANT_ITALIC
        else:
            slant = cairo.FONT_SLANT_NORMAL


        if text_line.bold:
            boldness = cairo.FONT_WEIGHT_BOLD
        else:
            boldness = cairo.FONT_WEIGHT_NORMAL
        
        canvas.select_font_face(text_line.font, slant, boldness)
        canvas.set_font_size(text_line.size)
        canvas.set_source_rgba(*self.cache_color(text_line.color))

        if text_style:
            (x, y, width, height, dx, dy) = canvas.text_extents(text_line.text)
            x_pos -= width/2
            y_pos += height/2

        canvas.move_to(x_pos, y_pos)
        canvas.show_text(text_line.text)
