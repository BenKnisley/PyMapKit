"""
Project: PyMapKit
Title: Tkinter Rendering Backend
Function: Define TkBackend class and contain all Tk drawing functionality.
Author: Ben Knisley [benknisley@gmail.com]
Created: 15 July, 2020
"""
from .base_backend import BaseBackend
import tkinter as tk
from PIL import Image, ImageTk

class TkBackend(BaseBackend):
    def new_canvas(self, width, height):
        self.surface = tk.Tk()
        canvas = tk.Canvas(self.surface, width=width, height=height)
        canvas.pack()
        self.surface.update()
        return canvas
    
    def is_canvas(self, target):
        return isinstance(target, tk.Canvas)
    
    def save(self, canvas, output):
        if output:
            self.surface.update()    
            canvas.postscript(file=output)
        else:
            self.surface.mainloop()

    def cache_image(self, image_path):
        return Image.open(image_path)

    def cache_color(self, input_color, opacity=1):
        ## Two types of color strings: Html color names and hex
        if isinstance(input_color, str):
            ##
            if input_color.lower() in BaseBackend.color_names:
                input_color = BaseBackend.color_names[input_color.lower()]


            if ('#' in input_color) and (len(input_color) == 7):
                return input_color
            elif input_color.lower() in color_dict:
                hex_string = color_dict[input_color.lower()]
                return hex_string
            else:
                return 'black'
        else:
            return 'black'

    def draw_background(self, canvas, color): #? Make sure background can be transparent
        canvas.configure(bg=color)
        canvas.create_rectangle(0,0,5000,5000, fill=color)

    def draw_point(self, canvas, structure, x_values, y_values, style):
        ## Cache colors
        if not style.cached_renderer:
            style.cache_renderer(self)
        elif style.cached_renderer != self:
            style.cache_renderer(self)
        
        pointer = 0
        for p_count in structure:
            for index in range(pointer, pointer+p_count):
                x1 = x_values[index] - style.weight 
                y1 = y_values[index] - style.weight
                x2 = x_values[index] + style.weight
                y2 = y_values[index] + style.weight
                canvas.create_oval(x1, y1, x2, y2, outline=style._outline_color_cache, width=style.outline_weight, fill=style._color_cache)
            pointer += p_count

    def draw_line(self, canvas, structure, x_values, y_values, style):
        ## Cache colors
        if not style.cached_renderer:
            style.cache_renderer(self)
        elif style.cached_renderer != self:
            style.cache_renderer(self)
        
        pointer = 0
        for p_count in structure:
            args = []
            x_coords = x_values[pointer:pointer+p_count]
            y_coords = y_values[pointer:pointer+p_count]
            for xy in zip(x_coords, y_coords):
                args.append(xy[0])
                args.append(xy[1])
            canvas.create_line(*args, fill=style._outline_color_cache, width=style.weight+style.outline_weight)
            canvas.create_line(*args, fill=style._color_cache, width=style.weight)
            pointer = pointer + p_count
    
    def draw_polygon(self, canvas, structure, x_values, y_values, style):
        ## Cache colors
        if not style.cached_renderer:
            style.cache_renderer(self)
        elif style.cached_renderer != self:
            style.cache_renderer(self)
        
        pointer = 0
        for p_count in structure:
            args = []
            x_coords = x_values[pointer:pointer+p_count]
            y_coords = y_values[pointer:pointer+p_count]
            for xy in zip(x_coords, y_coords):
                args.append(xy[0])
                args.append(xy[1])
            canvas.create_polygon(*args, fill=style._color_cache, outline=style._outline_color_cache, width=style.outline_weight)
            pointer = pointer + p_count

    def draw_image(self, canvas, image_cache, x, y, x_scale, y_scale, align='nw'):
        width, height = image_cache.size
        new_width = int(width * x_scale)
        new_height = int(height * y_scale)

        img = ImageTk.PhotoImage(image_cache.resize((new_width, new_height), Image.ANTIALIAS))

        if not hasattr(canvas, 'img_store'):
            canvas.img_store = []
        canvas.img_store.append(img)
        
        ## Draw image on
        canvas.create_image(x, y, image=img, anchor=align)
    
    def draw_text(self, canvas, text_line, x_pos, y_pos, text_style=None):
        effect_string = ''
        if text_line.italic:
            effect_string += 'italic '

        if text_line.bold:
            effect_string += 'bold '
        
        if text_style:
            align = 'center'
        else:
            align = 'nw'


        #if text_line.underline:
        #    effect_string += 'underline'
        effect_string = effect_string.strip()

        ## Draw Text
        canvas.create_text(x_pos, y_pos, font=(text_line.font, text_line.size, effect_string), text=text_line.text, fill=text_line.color, anchor=align)


