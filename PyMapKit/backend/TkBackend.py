"""
Project: PyMapKit
Title: Tkinter Rendering Backend
Function: Define TkBackend class and contain all Tk drawing functionality.
Author: Ben Knisley [benknisley@gmail.com]
Created: 15 July, 2020
"""
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk

class TkBackend:
    """
    """    
    def create_canvas(self, width, height):
        """ """
        self.surface = tk.Tk()
        canvas = tk.Canvas(self.surface, width=width, height=height)
        canvas.pack()
        self.surface.update()
        return canvas

    def can_render_to(self, target):
        """
        Returns if backend can render directly to target
        """
        return isinstance(target, tk.Canvas)

    def save(self, canvas, target):
        """ """
        if target:
            self.surface.update()    
            canvas.postscript(file=target)
        else:
            self.surface.mainloop()

    def color_converter(self, input_color):
        """ Converts different color formats into single format.

        Inputs:
            - "#0F0F0F" - A html color hex string.

            - "colorname" - A html color name string.

        Returns:
            - "#0F0F0F" - A html color hex string.

        """

        ## Define color dictionary, with html color names defined
        color_dict = {"aliceblue": "#f0f8ff", "antiquewhite": "#faebd7", "aqua": "#00ffff", "aquamarine": "#7fffd4", "azure": "#f0ffff", "beige": "#f5f5dc", "bisque": "#ffe4c4", "black": "#000000", "blanchedalmond": "#ffebcd", "blue": "#0000ff", "blueviolet": "#8a2be2", "brown": "#a52a2a", "burlywood": "#deb887", "cadetblue": "#5f9ea0", "chartreuse": "#7fff00", "chocolate": "#d2691e", "coral": "#ff7f50", "cornflowerblue": "#6495ed", "cornsilk": "#fff8dc", "crimson": "#dc143c", "cyan": "#00ffff", "darkblue": "#00008b", "darkcyan": "#008b8b", "darkgoldenrod": "#b8860b", "darkgray": "#a9a9a9", "darkgreen": "#006400", "darkkhaki": "#bdb76b", "darkmagenta": "#8b008b", "darkolivegreen": "#556b2f", "darkorange": "#ff8c00", "darkorchid": "#9932cc", "darkred": "#8b0000", "darksalmon": "#e9967a", "darkseagreen": "#8fbc8f", "darkslateblue": "#483d8b", "darkslategray": "#2f4f4f", "darkturquoise": "#00ced1", "darkviolet": "#9400d3", "deeppink": "#ff1493", "deepskyblue": "#00bfff", "dimgray": "#696969", "dodgerblue": "#1e90ff", "firebrick": "#b22222", "floralwhite": "#fffaf0", "forestgreen": "#228b22", "fuchsia": "#ff00ff", "gainsboro": "#dcdcdc", "ghostwhite": "#f8f8ff", "gold": "#ffd700", "goldenrod": "#daa520", "gray": "#808080", "green": "#008000", "greenyellow": "#adff2f", "honeydew": "#f0fff0", "hotpink": "#ff69b4", "indianred": "#cd5c5c", "indigo": "#4b0082", "ivory": "#fffff0", "khaki": "#f0e68c", "lavender": "#e6e6fa", "lavenderblush": "#fff0f5", "lawngreen": "#7cfc00", "lemonchiffon": "#fffacd", "lightblue": "#add8e6", "lightcoral": "#f08080", "lightcyan": "#e0ffff", "lightgoldenrodyellow": "#fafad2", "lightgray": "#d3d3d3", "lightgreen": "#90ee90", "lightpink": "#ffb6c1", "lightsalmon": "#ffa07a", "lightseagreen": "#20b2aa", "lightskyblue": "#87cefa", "lightslategray": "#778899", "lightsteelblue": "#b0c4de", "lightyellow": "#ffffe0", "lime": "#00ff00", "limegreen": "#32cd32", "linen": "#faf0e6", "magenta": "#ff00ff", "maroon": "#800000", "mediumaquamarine": "#66cdaa", "mediumblue": "#0000cd", "mediumorchid": "#ba55d3", "mediumpurple": "#9370d8", "mediumseagreen": "#3cb371", "mediumslateblue": "#7b68ee", "mediumspringgreen": "#00fa9a", "mediumturquoise": "#48d1cc", "mediumvioletred": "#c71585", "midnightblue": "#191970", "mintcream": "#f5fffa", "mistyrose": "#ffe4e1", "moccasin": "#ffe4b5", "navajowhite": "#ffdead", "navy": "#000080", "oldlace": "#fdf5e6", "olive": "#808000", "olivedrab": "#6b8e23", "orange": "#ffa500", "orangered": "#ff4500", "orchid": "#da70d6", "palegoldenrod": "#eee8aa", "palegreen": "#98fb98", "paleturquoise": "#afeeee", "palevioletred": "#db7093", "papayawhip": "#ffefd5", "peachpuff": "#ffdab9", "peru": "#cd853f", "pink": "#ffc0cb", "plum": "#dda0dd", "powderblue": "#b0e0e6", "purple": "#800080", "red": "#ff0000", "rosybrown": "#bc8f8f", "royalblue": "#4169e1", "saddlebrown": "#8b4513", "salmon": "#fa8072", "sandybrown": "#f4a460", "seagreen": "#2e8b57", "seashell": "#fff5ee", "sienna": "#a0522d", "silver": "#c0c0c0", "skyblue": "#87ceeb", "slateblue": "#6a5acd", "slategray": "#708090", "snow": "#fffafa", "springgreen": "#00ff7f", "steelblue": "#4682b4", "tan": "#d2b48c", "teal": "#008080", "thistle": "#d8bfd8", "tomato": "#ff6347", "turquoise": "#40e0d0", "violet": "#ee82ee", "wheat": "#f5deb3", "white": "#ffffff", "whitesmoke": "#f5f5f5", "yellow": "#ffff00", "yellowgreen": "#9acd32"}

        if ('#' in input_color) and (len(input_color) == 7):
            return input_color
        elif input_color.lower() in color_dict:
            hex_string = color_dict[input_color.lower()]
            return hex_string
        else:
            return 'black'

    def draw_background(self, canvas, color):
        ''' '''
        canvas.configure(bg=color)
        canvas.create_rectangle(0,0,5000,5000, fill=color)

    def draw_point(self, canvas, geomstruct, x_values, y_values, color, radius, alpha):
        """ """
        pointer = 0
        for p_count in geomstruct:
            for index in range(pointer, pointer+p_count):
                x1 = x_values[index] - radius 
                y1 = y_values[index] - radius
                x2 = x_values[index] + radius
                y2 = y_values[index] + radius
                canvas.create_oval(x1, y1, x2, y2, width=0, fill=color)
            pointer += p_count

    def draw_line(self, canvas, geomstruct, x_values, y_values, l_weight, l_color, alpha):
        """ """
        pointer = 0
        for p_count in geomstruct:
            args = []
            x_coords = x_values[pointer:pointer+p_count]
            y_coords = y_values[pointer:pointer+p_count]
            for xy in zip(x_coords, y_coords):
                args.append(xy[0])
                args.append(xy[1])
            canvas.create_line(*args, fill=l_color, width=l_weight)
            pointer = pointer + p_count

    def draw_polygon(self, canvas, geomstruct, x_values, y_values, bg_color, l_weight, l_color, alpha):
        """ """
        pointer = 0
        for p_count in geomstruct:
            args = []
            x_coords = x_values[pointer:pointer+p_count]
            y_coords = y_values[pointer:pointer+p_count]
            for xy in zip(x_coords, y_coords):
                args.append(xy[0])
                args.append(xy[1])
            canvas.create_polygon(*args, fill=bg_color, outline=l_color, width=l_weight)
            pointer = pointer + p_count

    def get_image_obj(self, path):
        ''' '''
        return Image.open(path)

    def draw_image(self, canvas, img_reference, TL_x, TL_y, scale_x, scale_y):
        width, height = img_reference.size
        new_width = int(width * scale_x)
        new_height = int(height * scale_y)

        img = ImageTk.PhotoImage(img_reference.resize((new_width, new_height), Image.ANTIALIAS))

        if not hasattr(canvas, 'img_store'):
            canvas.img_store = []
        canvas.img_store.append(img)
        
        ## Draw image on
        canvas.create_image(TL_x, TL_y, image=img, anchor='nw')

    def draw_text(self, canvas, text_line, x_pos, y_pos):
        effect_string = ''
        if text_line.italic:
            effect_string += 'italic '

        if text_line.bold:
            effect_string += 'bold '
        
        #if text_line.underline:
        #    effect_string += 'underline'
        effect_string = effect_string.strip()

        ## Draw Text
        canvas.create_text(x_pos, y_pos, font=(text_line.font, text_line.size, effect_string), text=text_line.text, fill=text_line.color, anchor='nw')
