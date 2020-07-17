"""
Project: PyMapKit
Title: Cairo Rendering Backend
Function: Define CairoBackend class and contain all cairo drawing functionality.
Author: Ben Knisley [benknisley@gmail.com]
Created: 1 January, 2020
"""
import numpy as np
import cairo

class CairoBackend:
    def __init__(self):
        pass

    def create_canvas(self, width, height):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        canvas = cairo.Context(self.surface)
        return canvas

    def can_render_to(self, target):
        """
        Returns if backend can render directly to target
        """
        return isinstance(target, cairo.Context)

    def save(self, canvas, target):
        """ 
        Backend has to support target being None
        """
        if target:
            self.surface.write_to_png(target)

    def color_converter(self, input_color):
        """ Converts different color formats into single format.

        Inputs:
            - (float, float, float) - A tuple of three floats between 0.0 and 1.0
                representing red, green, & blue values respectively.

            - (int, int, int) - A tuple of three ints between 0 and 1
                representing red, green, & blue values respectively.

            - "#0F0F0F" - A html color hex string.

            - "colorname" - A html color name.

        Returns:
            - (float, float, float) - A tuple of three floats between 0.0 and 1.0
                representing red, green, & blue values respectively.

        """
        ## Two tuple types, 0-1 or 0-256
        if isinstance(input_color, tuple):

            ## If float tuple, input same as output
            if isinstance(input_color[0], float):
                return input_color

            if isinstance(input_color[0], int):
                R = input_color[3] / 255.0
                G = input_color[5] / 255.0
                B = input_color[7] / 255.0
                return (R,G,B)

        ## Two types of color strings: Html color names and hex
        if isinstance(input_color, str):
            ## Define color dictionary, with html color names defined
            color_dict = {"aliceblue": "#f0f8ff", "antiquewhite": "#faebd7", "aqua": "#00ffff", "aquamarine": "#7fffd4", "azure": "#f0ffff", "beige": "#f5f5dc", "bisque": "#ffe4c4", "black": "#000000", "blanchedalmond": "#ffebcd", "blue": "#0000ff", "blueviolet": "#8a2be2", "brown": "#a52a2a", "burlywood": "#deb887", "cadetblue": "#5f9ea0", "chartreuse": "#7fff00", "chocolate": "#d2691e", "coral": "#ff7f50", "cornflowerblue": "#6495ed", "cornsilk": "#fff8dc", "crimson": "#dc143c", "cyan": "#00ffff", "darkblue": "#00008b", "darkcyan": "#008b8b", "darkgoldenrod": "#b8860b", "darkgray": "#a9a9a9", "darkgreen": "#006400", "darkkhaki": "#bdb76b", "darkmagenta": "#8b008b", "darkolivegreen": "#556b2f", "darkorange": "#ff8c00", "darkorchid": "#9932cc", "darkred": "#8b0000", "darksalmon": "#e9967a", "darkseagreen": "#8fbc8f", "darkslateblue": "#483d8b", "darkslategray": "#2f4f4f", "darkturquoise": "#00ced1", "darkviolet": "#9400d3", "deeppink": "#ff1493", "deepskyblue": "#00bfff", "dimgray": "#696969", "dodgerblue": "#1e90ff", "firebrick": "#b22222", "floralwhite": "#fffaf0", "forestgreen": "#228b22", "fuchsia": "#ff00ff", "gainsboro": "#dcdcdc", "ghostwhite": "#f8f8ff", "gold": "#ffd700", "goldenrod": "#daa520", "gray": "#808080", "green": "#008000", "greenyellow": "#adff2f", "honeydew": "#f0fff0", "hotpink": "#ff69b4", "indianred": "#cd5c5c", "indigo": "#4b0082", "ivory": "#fffff0", "khaki": "#f0e68c", "lavender": "#e6e6fa", "lavenderblush": "#fff0f5", "lawngreen": "#7cfc00", "lemonchiffon": "#fffacd", "lightblue": "#add8e6", "lightcoral": "#f08080", "lightcyan": "#e0ffff", "lightgoldenrodyellow": "#fafad2", "lightgray": "#d3d3d3", "lightgreen": "#90ee90", "lightpink": "#ffb6c1", "lightsalmon": "#ffa07a", "lightseagreen": "#20b2aa", "lightskyblue": "#87cefa", "lightslategray": "#778899", "lightsteelblue": "#b0c4de", "lightyellow": "#ffffe0", "lime": "#00ff00", "limegreen": "#32cd32", "linen": "#faf0e6", "magenta": "#ff00ff", "maroon": "#800000", "mediumaquamarine": "#66cdaa", "mediumblue": "#0000cd", "mediumorchid": "#ba55d3", "mediumpurple": "#9370d8", "mediumseagreen": "#3cb371", "mediumslateblue": "#7b68ee", "mediumspringgreen": "#00fa9a", "mediumturquoise": "#48d1cc", "mediumvioletred": "#c71585", "midnightblue": "#191970", "mintcream": "#f5fffa", "mistyrose": "#ffe4e1", "moccasin": "#ffe4b5", "navajowhite": "#ffdead", "navy": "#000080", "oldlace": "#fdf5e6", "olive": "#808000", "olivedrab": "#6b8e23", "orange": "#ffa500", "orangered": "#ff4500", "orchid": "#da70d6", "palegoldenrod": "#eee8aa", "palegreen": "#98fb98", "paleturquoise": "#afeeee", "palevioletred": "#db7093", "papayawhip": "#ffefd5", "peachpuff": "#ffdab9", "peru": "#cd853f", "pink": "#ffc0cb", "plum": "#dda0dd", "powderblue": "#b0e0e6", "purple": "#800080", "red": "#ff0000", "rosybrown": "#bc8f8f", "royalblue": "#4169e1", "saddlebrown": "#8b4513", "salmon": "#fa8072", "sandybrown": "#f4a460", "seagreen": "#2e8b57", "seashell": "#fff5ee", "sienna": "#a0522d", "silver": "#c0c0c0", "skyblue": "#87ceeb", "slateblue": "#6a5acd", "slategray": "#708090", "snow": "#fffafa", "springgreen": "#00ff7f", "steelblue": "#4682b4", "tan": "#d2b48c", "teal": "#008080", "thistle": "#d8bfd8", "tomato": "#ff6347", "turquoise": "#40e0d0", "violet": "#ee82ee", "wheat": "#f5deb3", "white": "#ffffff", "whitesmoke": "#f5f5f5", "yellow": "#ffff00", "yellowgreen": "#9acd32"}

            if input_color.lower() in color_dict:
                input_color = color_dict[input_color.lower()]


            if '#' in input_color and len(input_color) == 7:
                ## Hex string color
                R = int(input_color[1:3], 16) / 255.0
                G = int(input_color[3:5], 16) / 255.0
                B = int(input_color[5:7], 16) / 255.0
                return (R,G,B)

    def draw_background(self, cr, color):
        ## Draw background
        cr.set_source_rgba(*self.color_converter(color))
        cr.paint()

    def draw_point(self, cr, geomstruct, x_values, y_values, color, radius, alpha):
        """ """
        pointer = 0
        for p_count in geomstruct:
            for index in range(pointer, pointer+p_count):
                cr.set_source_rgba(*color, alpha)
                cr.arc(x_values[index], y_values[index], radius, 0, 6.2830)
                cr.fill()
            pointer += p_count

    def draw_line(self, cr, geomstruct, x_values, y_values, l_weight, l_color, alpha):
        """ """
        cr.set_source_rgba(*l_color, alpha)
        cr.set_line_width(l_weight)
        pointer = 0
        for p_count in geomstruct:
            cr.move_to( x_values[pointer], y_values[pointer] )
            for index in range(pointer, pointer+p_count):
                cr.line_to( x_values[index], y_values[index] )
            cr.stroke()
            pointer += p_count

    def draw_polygon(self, cr, geomstruct, x_values, y_values, bg_color, l_weight, l_color, alpha):
        """ """
        pointer = 0
        for p_count in geomstruct:
            cr.move_to( x_values[pointer], y_values[pointer] )

            for index in range(pointer, pointer+p_count):
                cr.line_to(x_values[index], y_values[index])
            pointer = pointer + p_count

        cr.set_source_rgba(*bg_color, alpha)
        cr.fill_preserve()
        cr.set_source_rgba(*l_color, alpha)
        cr.set_line_width(l_weight)
        cr.stroke()

    def get_image_obj(self, path):
        ''' '''
        return cairo.ImageSurface.create_from_png(path)

    def draw_image(self, cr, img_surface, pix_x, pix_y, scale_x, scale_y):
        """ """
        cr.save()
        cr.translate(pix_x, pix_y)
        cr.scale(scale_x, scale_x)
        cr.set_source_surface(img_surface, 0, 0)
        cr.paint()
        cr.restore()

    def draw_text(self, cr, text_line, x_pos, y_pos):
        """ """
        if text_line.italic:
            slant = cairo.FONT_SLANT_ITALIC
        else:
            slant = cairo.FONT_SLANT_NORMAL


        if text_line.bold:
            boldness = cairo.FONT_WEIGHT_BOLD
        else:
            boldness = cairo.FONT_WEIGHT_NORMAL

        
        cr.select_font_face(text_line.font, slant, boldness)
        cr.set_font_size(text_line.size)
        cr.set_source_rgba(*self.color_converter(text_line.color), 1)

        cr.move_to(x_pos, y_pos)
        cr.show_text(text_line.text)
