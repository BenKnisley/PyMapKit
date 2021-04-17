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
        Converts a given color to a Skia color 

        Converts a given color to an integer representing that color to Skia.

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
        """
        Draws a single color on the whole canvas.
        
        Args:
            canvas (skia.Canvas): The canvas to draw on.

            color (*): A object representing the color to use.

        Returns:
            None
        """
        ## If given color is not in skia format (int), convert it.
        if not isinstance(color, int):
            color = self.cache_color(color)

        ## Create a Skia Paint object and draw paint over whole canvas
        paint = skia.Paint(Color=color)
        canvas.drawPaint(paint)
    

    
    ##
    ##
    ##

    def draw_point(self, canvas, structure, x_values, y_values, style):
        """
        Draws a point or mutipoint onto the canvas.

        Args:
            canvas (skia.Canvas): The canvas to draw on.

            structure (List): A list holding the structure of the geometry. 

            x_values (List): A List holding the pixel x values.
            
            y_values (List): A List holding the pixel y values.

            style (vector_layer.FeatureStyle): Object storing style infomation.
        
        Returns:
            None
        """
        ## Cache colors if color is not cached
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
        """
        Draws a line or mutiline onto the canvas.

        Args:
            canvas (skia.Canvas): The canvas to draw on.

            structure (List): A list holding the structure of the geometry. 

            x_values (List): A List holding the pixel x values.
            
            y_values (List): A List holding the pixel y values.

            style (vector_layer.FeatureStyle): Object storing style infomation.
        
        Returns:
            None
        """
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
        """
        Draws a polygon or mutipolygon onto the canvas.

        Args:
            canvas (skia.Canvas): The canvas to draw on.

            structure (List): A list holding the structure of the geometry. 

            x_values (List): A List holding the pixel x values.
            
            y_values (List): A List holding the pixel y values.

            style (vector_layer.FeatureStyle): Object storing style infomation.
        
        Returns:
            None
        """
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
    
    ##
    ##
    ##

    def cache_image(self, image_path):
        """
        Loads image data into memory, and providing a cached image object.

        Args:
            image_path (str): The path to the image.
        
        Returns:
            cache_image (skia.Image): The cached image object.
        """
        return skia.Image.open(image_path)


    def draw_image(self, canvas, image_cache, x, y, x_scale, y_scale, align='nw'):
        """
        Draws a image onto the canvas.

        Args:
           canvas (skia.Canvas): The canvas to draw on.

           image_cache (skia.Image): The cached image to draw.

           x (int): The pixel x location to place the image (see align arg).
           
           y (int): The pixel y location to place the image (see align arg).

           x_scale (float): The scaling factor in the x direction.
           
           y_scale (float): The scaling factor in the y direction.

        Optional Args:
            align (str): Code for where to anchor the image (uses cardinal 
            directions).

        Returns:
            None
        """
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
    
    ##
    ##
    ##

    def draw_text(self, canvas, text, text_style):
        pass