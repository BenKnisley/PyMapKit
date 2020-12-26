"""
Project: PyMapKit
Title: Skia Rendering Backend
Function: Define SkiaBackend class and contain all Skia drawing functionality.
Author: Ben Knisley [benknisley@gmail.com]
Created: 18 December, 2020
"""
from .base_backend import BaseBackend
import skia

class SkiaBackend(BaseBackend):
    def new_canvas(self, width, height):
        self.surface = skia.Surface(width, height)
        canvas = self.surface.getCanvas()
        return canvas
    
    def is_canvas(self, target):
        return isinstance(target, skia.Surface)
    
    def save(self, canvas, output):
        if output:
            image = self.surface.makeImageSnapshot()
            image.save(output, skia.kPNG)

    def cache_image(self, image_path):
        return skia.Image.open(image_path)

    def cache_color(self, input_color, opacity=1):
        ## Two tuple types, 0-1 or 0-256
        if isinstance(input_color, tuple):
            if isinstance(input_color[0], float):
                rtrn_color = *input_color, opacity
                return skia.Color(*rtrn_color)
                R = int(input_color[3] * 255.0)
                G = int(input_color[5] * 255.0)
                B = int(input_color[7] * 255.0)
                A = int(opacity * 255)
                return skia.Color(R,G,B,A)

            elif isinstance(input_color[0], int):
                R = int(input_color[3])
                G = int(input_color[5])
                B = int(input_color[7])
                A = int(opacity * 255)
                return skia.Color(R,G,B,A)

        ## Two types of color strings: Html color names and hex
        if isinstance(input_color, str):
            ##
            if input_color.lower() in BaseBackend.color_names:
                input_color = BaseBackend.color_names[input_color.lower()]

            if '#' in input_color and len(input_color) == 7:
                ## Hex string color
                R = int(int(input_color[1:3], 16))
                G = int(int(input_color[3:5], 16))
                B = int(int(input_color[5:7], 16))
                A = int(opacity * 255)
                return skia.Color(R,G,B,A)

    def draw_background(self, canvas, color):
        if not isinstance(color, int):
            color = self.cache_color(color)

        paint = skia.Paint(Color=color)
        canvas.drawPaint(paint)

    def draw_point(self, canvas, structure, x_values, y_values, style):
        ## Cache colors
        if not style.cached_renderer:
            style.cache_renderer(self)
        elif style.cached_renderer != self:
            style.cache_renderer(self)
        
        ## Create a path
        path = skia.Path()

        ## Add points to path
        pointer = 0
        for p_count in structure:
            for index in range(pointer, pointer+p_count):
                path.addCircle(x_values[index], y_values[index], style.weight)
            pointer += p_count
        
        ## Draw background
        paint = skia.Paint(AntiAlias=True)
        paint.setColor(style._color_cache)
        canvas.drawPath(path, paint)
        
        ## Draw outline
        paint.setStyle(skia.Paint.kStroke_Style)
        paint.setColor(style._outline_color_cache)
        paint.setStrokeWidth(style.outline_weight)
        canvas.drawPath(path, paint)

    def draw_line(self, canvas, structure, x_values, y_values, style):
        ## Cache colors
        if not style.cached_renderer:
            style.cache_renderer(self)
        elif style.cached_renderer != self:
            style.cache_renderer(self)

        ## Create a path
        path = skia.Path()

        ## Load points into path
        pointer = 0
        for p_count in structure:
            path.moveTo( x_values[pointer], y_values[pointer] )
            for index in range(pointer, pointer+p_count):
                path.lineTo( x_values[index], y_values[index] )
            pointer += p_count
        
        ## Create outline paint
        paint = skia.Paint(style._outline_color_cache)
        paint.setStyle(skia.Paint.kStroke_Style)
        paint.setStrokeWidth(style.weight+style.outline_weight)
        paint.setAntiAlias(True)

        ## Draw outline path
        canvas.drawPath(path, paint)

        ## Create line paint
        paint = skia.Paint(style._color_cache)
        paint.setStyle(skia.Paint.kStroke_Style)
        paint.setStrokeWidth(style.weight)
        paint.setAntiAlias(True)

        ## Draw line path
        canvas.drawPath(path, paint)

    def draw_polygon(self, canvas, structure, x_values, y_values, style):
        ## Cache colors
        if not style.cached_renderer:
            style.cache_renderer(self)
        elif style.cached_renderer != self:
            style.cache_renderer(self)

        ## Create a path
        path = skia.Path()

        ## Load points into path
        pointer = 0
        for p_count in structure:
            path.moveTo( x_values[pointer], y_values[pointer] )

            for index in range(pointer, pointer+p_count):
                path.lineTo(x_values[index], y_values[index])
            pointer = pointer + p_count

        ## Draw feature background
        paint = skia.Paint(style._color_cache)
        paint.setAntiAlias(True)
        canvas.drawPath(path, paint)

        ## Draw feature outline
        paint.setStyle(skia.Paint.kStroke_Style)
        paint.setColor(style._outline_color_cache)
        paint.setStrokeWidth(style.outline_weight)
        canvas.drawPath(path, paint)

    def draw_image(self, canvas, image_cache, x, y, x_scale, y_scale, align='nw'):
        #def draw_image(self, cr, img_surface, pix_x, pix_y, scale_x, scale_y):
        if align != 'nw':
            if align[0] == 'c': ## Center
                x -= int((image_cache.get_width() * x_scale) / 2.0)
                y -= int((image_cache.get_height() * y_scale) / 2.0)
            else:
                pass #! ADD MORE
        
        ## Get width of image
        w = image_cache.width()
        h = image_cache.height()

        ## Create a scaled rectangle
        rect = skia.Rect.MakeXYWH(x,y, int(w * x_scale), int(h * y_scale))

        ## Draw image
        canvas.drawImageRect(image_cache, rect)
    
    def draw_text(self, canvas, text_line, x_pos, y_pos, text_style=None):
        """ """
        ## Create a list to hold Typeface constructor args
        typeface_args = [text_line.font]

        ## Append FontStyle objects to list depending on params
        if text_line.italic and text_line.bold:
            typeface_args.append(skia.FontStyle.BoldItalic())
        elif text_line.bold:
            typeface_args.append(skia.FontStyle.Bold())
        elif text_line.italic:
            typeface_args.append(skia.FontStyle.Italic())            

        ## Create FontStyle object from constructor args
        typeface = skia.Typeface(*typeface_args)

        ## Create a font and set params
        font = skia.Font()
        font.setSize(float(text_line.size))
        font.setTypeface( typeface )

        ## Create a paint object
        paint = skia.Paint(self.cache_color(text_line.color))
        
        if text_style:
            width = font.measureText(text_line.text)
            height = font.getSize() * 1.334 #! I really hate this hack
            x_pos -= width/2
            y_pos += height/2

        ## Draw Text Line!
        canvas.drawSimpleText(text_line.text, x_pos, y_pos, font, paint)