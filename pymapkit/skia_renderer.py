"""
Project: PyMapKit
File: skia_renderer.py
Title: Skia Renderer Class
Function: Implements the drawing api using the PySkia library.
Author: Ben Knisley [benknisley@gmail.com]
Created: 5 February, 2021
"""
import functools
import skia
from .base_renderer import BaseRenderer


class SkiaRenderer(BaseRenderer):
    """
    Derived from the BaseRenderer abstract class, SkiaRenderer is an 
    implementation of the drawing API using the Skia-Python library.
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

    def draw_background(self, canvas, style):
        """
        Draws a single color on the whole canvas.
        
        Args:
            canvas (skia.Canvas): The canvas to draw on.

            color (*): A object representing the color to use.

        Returns:
            None
        """

        ## If a rendering function is already defined, use it.
        if style.cached_renderer_fn:
            style.cached_renderer_fn(canvas)
            return
        
        if style['background_mode'] == 'none':
            return

        color = self.cache_color(style['background_color'], style['background_opacity'])

        draw_background_basic(canvas, color)
        style.cached_renderer_fn = cache_fn(draw_background_basic, color=color)

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

        ## Create a point list
        point_list = []

        ## Add points to path
        pointer = 0
        for p_count in structure:
            for index in range(pointer, pointer+p_count):
                point_list.append((x_values[index], y_values[index]))
            pointer += p_count

        ## If a rendering function is already cached, use it.
        if style.cached_renderer_fn:
            style.cached_renderer_fn(canvas, point_list)
            return

        
        ## Fill
        if  style['mode'] == 'none':
            ## Cache em
            fill_cached_renderer_fn = empty_fn()

        elif style['mode'] == 'circle':
            ## Pull relevant data from style
            color = self.cache_color(style['color'], style['opacity'])
            weight = style['weight'] / 2
            
            ## Draw point, & cache function and parameters for rendering
            draw_point_circle(canvas, point_list, color, weight)
            style.cached_renderer_fn = cache_fn(draw_point_circle, color=color, weight=weight)
        
        else:
            print(f'''"{style['mode']}" display mode not yet supported by this renderer''')

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

        ## Create skia path object
        path = skia.Path()

        ## Load points into path
        pointer = 0
        for p_count in structure:
            path.moveTo( x_values[pointer], y_values[pointer] )
            for index in range(pointer, pointer+p_count):
                path.lineTo(x_values[index], y_values[index])
            pointer = pointer + p_count

        ## If a rendering function is already defined, use it.
        if style.cached_renderer_fn:
            style.cached_renderer_fn(canvas, path)
            return

                ## Fill
        if  style['mode'] == 'none':
            style.cached_renderer_fn = empty_fn()

        elif style['mode'] == 'solid':
            color = self.cache_color(style['color'], style['opacity'])
            weight = style['weight'] / 2

            draw_line_solid(canvas, path, color, weight)
            style.cached_renderer_fn = cache_fn(draw_line_solid, color=color, weight=weight)

        elif style['mode'] == 'dashed':
            color = self.cache_color(style['color'], style['opacity'])
            weight = style['weight'] / 2

            draw_line_dashed(canvas, path, color, weight)
            style.cached_renderer_fn = cache_fn(draw_line_dashed, color=color, weight=weight)
        
        else:
            pass
            return

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

        ## Create skia path object
        path = skia.Path()

        ## Load points into path
        pointer = 0
        for p_count in structure:
            path.moveTo( x_values[pointer], y_values[pointer] )
            for index in range(pointer, pointer+p_count):
                path.lineTo(x_values[index], y_values[index])
            pointer = pointer + p_count

        ## If a rendering function is already cached, use it.
        if style.cached_renderer_fn:
            style.cached_renderer_fn(canvas, path)
            return
        

        ## Whole feature none display override
        if style['display'] in ('none', False, None):
            style.cached_renderer_fn = empty_fn()
            return

        ## Fill
        if style['fill_mode'] == 'none':
            fill_cached_renderer_fn = empty_fn()

        elif style['fill_mode'] == 'basic':
            total_opacity = style['opacity'] * style['fill_opacity']
            fill_color = self.cache_color(style['fill_color'], total_opacity)
            draw_poly_basic_fill(canvas, path, fill_color)
            fill_cached_renderer_fn = cache_fn(draw_poly_basic_fill, fill_color=fill_color)
        
        elif style['fill_mode'] == 'line':
            fill_line_color = self.cache_color(style['fill_line_color'], style['fill_line_opacity'])
            draw_poly_line_fill(canvas, path, fill_line_color)
            fill_cached_renderer_fn = cache_fn(draw_poly_line_fill, fill_line_color=fill_line_color)

        elif style['fill_mode'] == 'image':
            image_cache = self.cache_image(style['fill_image_path'])
            draw_poly_image_fill(canvas, path, image_cache)
            fill_cached_renderer_fn = cache_fn(draw_poly_image_fill, image_cache=image_cache)

        else:
            pass
        
        ## Outline
        if  style['outline_mode'] == 'none':
            outline_cached_renderer_fn = empty_fn()

        elif style['outline_mode'] == 'solid':
            total_opacity = style['opacity'] * style['outline_opacity']
            outline_color = self.cache_color(style['outline_color'], total_opacity)
            outline_weight = style['outline_weight']
            draw_poly_solid_outline(canvas, path, outline_color, outline_weight)
            outline_cached_renderer_fn = cache_fn(draw_poly_solid_outline, outline_color=outline_color, outline_weight=outline_weight)


        style.cached_renderer_fn = join_fns((fill_cached_renderer_fn, outline_cached_renderer_fn))

    def cache_image(self, image_path):
        """
        Loads image data into memory, and providing a cached image object.

        Args:
            image_path (str): The path to the image.
        
        Returns:
            cache_image (skia.Image): The cached image object.
        """
        return skia.Image.open(image_path)

    def draw_image(self, canvas, image_cache, x, y, x_scale, y_scale, align='nw', opacity=1):
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

            opacity (float): Value 0-1 indicating opacity of image.

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

        ## Create a paint object for opacity 
        paint = skia.Paint(Alphaf=opacity)
        
        ## Draw image
        canvas.drawImageRect(image_cache, rect, paint)

    def draw_text(self, canvas, text, x, y, style):

        paint = skia.Paint()
        paint.setColor( self.cache_color(style['color']) )    
        
        font = skia.Font()
        font.setSize(style['font_size'])


        canvas.drawSimpleText(text, x, y, font, paint)




"""****************************
****** Caching functions ******
****************************"""

def cache_fn(fn, **args):
    """
    """
    _args = args
    cached_fn = functools.partial(fn, **_args)
    return cached_fn

def join_fns(functions):
    def inner(canvas, path):
        for fn in functions:
            fn(canvas, path)
    return inner

def empty_fn():
    def fun(*args): 
        pass
    return fun

"""****************************
****** Drawing functions ******
****************************"""

## Background display Modes

def draw_background_basic(canvas, color):
    """
    Fills the whole canvas with a solid color.
    """
    ## Create a Skia Paint object and draw paint over whole canvas
    paint = skia.Paint(Color=color)
    canvas.drawPaint(paint)

## Point Display Modes

def draw_point_circle(canvas, point_list, color, weight):
    
    paint = skia.Paint(AntiAlias=True)
    paint.setColor(color)


    for point in point_list:
         path = skia.Path()
         path.addCircle(point[0], point[1], weight)
         canvas.drawPath(path, paint)

    return

## Line Display modes

def draw_line_solid(canvas, path, color, weight):
     ## Create line paint
    paint = skia.Paint(color)
    paint.setStyle(skia.Paint.kStroke_Style)
    paint.setStrokeWidth(weight)
    paint.setAntiAlias(True)

    ## Draw line path
    canvas.drawPath(path, paint)

def draw_line_dashed(canvas, path, color, weight):
        paint = skia.Paint(
            Color=color,
            AntiAlias=True,
            PathEffect=skia.DashPathEffect.Make([weight*5, 10], 0),
            #PathEffect=skia.DashPathEffect.Make([weight, weight*2], 1), ## Dotted
            Style=skia.Paint.kStroke_Style,
        )
        paint.setStrokeWidth(weight)

        ## Draw line path
        canvas.drawPath(path, paint)


## Polygon Display Modes

def draw_poly_basic_fill(canvas, path, fill_color):
    """
    Fills a given Skia path with a single color.
    """
    ## Create paint object
    paint = skia.Paint(fill_color)
    paint.setAntiAlias(True)
    canvas.drawPath(path, paint)

def draw_poly_image_fill(canvas, path, image_cache):
    
    x1,y1, x2, y2 = path.getBounds()


    ## Get width of image
    w = image_cache.width()
    h = image_cache.height()

    ## Create a scaled rectangle

    canvas.save()

    canvas.clipPath(path)
    canvas.resetMatrix()
    #canvas.drawImage(image_data, x,y, paint)

    ## Create a paint object for opacity 
    #paint = skia.Paint(Alphaf=opacity)
    paint = skia.Paint()
    paint.setAntiAlias(True)
    rect = skia.Rect.MakeXYWH(x1, y1, x2-x1, y2-y1)
    canvas.drawImageRect(image_cache, rect, paint)

    canvas.restore()


def draw_poly_line_fill(canvas, path, fill_line_color):
    """
    Fills a given Skia path with a line fill.
    """
    ## Draw feature background
    lattice = skia.Matrix()
    lattice.setScale(4.0, 4.0)
    lattice.preRotate(30.0)
    paint = skia.Paint(PathEffect=skia.Line2DPathEffect.Make(0.0, lattice))
    paint.setAntiAlias(True)
    paint.setColor(fill_line_color)
    canvas.drawPath(path, paint)

def draw_poly_solid_outline(canvas, path, outline_color, outline_weight):
    paint = skia.Paint(outline_color)
    paint.setStrokeWidth(outline_weight)
    paint.setAntiAlias(True)
    paint.setStyle(skia.Paint.kStroke_Style)
    canvas.drawPath(path, paint)

