"""
Author: Ben Knisley [benknisley@gmail.com]
Date:
"""
import abc

class BaseRenderer(metaclass=abc.ABCMeta):
    color_names = {
        "aliceblue": "#f0f8ff", 
        "antiquewhite": "#faebd7", 
        "aqua": "#00ffff", 
        "aquamarine": "#7fffd4", 
        "azure": "#f0ffff", 
        "beige": "#f5f5dc", 
        "bisque": "#ffe4c4", 
        "black": "#000000", 
        "blanchedalmond": "#ffebcd", 
        "blue": "#0000ff", 
        "blueviolet": "#8a2be2", 
        "brown": "#a52a2a", 
        "burlywood": "#deb887", 
        "cadetblue": "#5f9ea0", 
        "chartreuse": "#7fff00", 
        "chocolate": "#d2691e", 
        "coral": "#ff7f50", 
        "cornflowerblue": "#6495ed", 
        "cornsilk": "#fff8dc", 
        "crimson": "#dc143c", 
        "cyan": "#00ffff", 
        "darkblue": "#00008b", 
        "darkcyan": "#008b8b", 
        "darkgoldenrod": "#b8860b", 
        "darkgray": "#a9a9a9", 
        "darkgreen": "#006400", 
        "darkkhaki": "#bdb76b", 
        "darkmagenta": "#8b008b", 
        "darkolivegreen": "#556b2f", 
        "darkorange": "#ff8c00", 
        "darkorchid": "#9932cc", 
        "darkred": "#8b0000", 
        "darksalmon": "#e9967a", 
        "darkseagreen": "#8fbc8f", 
        "darkslateblue": "#483d8b", 
        "darkslategray": "#2f4f4f", 
        "darkturquoise": "#00ced1", 
        "darkviolet": "#9400d3", 
        "deeppink": "#ff1493", 
        "deepskyblue": "#00bfff", 
        "dimgray": "#696969", 
        "dodgerblue": "#1e90ff", 
        "firebrick": "#b22222", 
        "floralwhite": "#fffaf0", 
        "forestgreen": "#228b22", 
        "fuchsia": "#ff00ff", 
        "ghostwhite": "#f8f8ff", 
        "gold": "#ffd700", 
        "goldenrod": "#daa520", 
        "gray": "#808080", 
        "green": "#008000", 
        "greenyellow": "#adff2f", 
        "honeydew": "#f0fff0", 
        "hotpink": "#ff69b4", 
        "indigo": "#4b0082", 
        "ivory": "#fffff0", 
        "khaki": "#f0e68c", 
        "lavender": "#e6e6fa", 
        "lavenderblush": "#fff0f5", 
        "lawngreen": "#7cfc00", 
        "lemonchiffon": "#fffacd", 
        "lightblue": "#add8e6", 
        "lightcoral": "#f08080", 
        "lightcyan": "#e0ffff", 
        "lightgoldenrodyellow": "#fafad2", 
        "lightgray": "#d3d3d3", 
        "lightgreen": "#90ee90", 
        "lightpink": "#ffb6c1", 
        "lightsalmon": "#ffa07a", 
        "lightseagreen": "#20b2aa", 
        "lightskyblue": "#87cefa", 
        "lightslategray": "#778899", 
        "lightsteelblue": "#b0c4de", 
        "lightyellow": "#ffffe0", 
        "lime": "#00ff00", 
        "limegreen": "#32cd32", 
        "linen": "#faf0e6", 
        "magenta": "#ff00ff", 
        "maroon": "#800000", 
        "mediumaquamarine": "#66cdaa", 
        "mediumblue": "#0000cd", 
        "mediumorchid": "#ba55d3", 
        "mediumpurple": "#9370d8", 
        "mediumseagreen": "#3cb371", 
        "mediumslateblue": "#7b68ee", 
        "mediumspringgreen": "#00fa9a", 
        "mediumturquoise": "#48d1cc", 
        "mediumvioletred": "#c71585", 
        "midnightblue": "#191970", 
        "mintcream": "#f5fffa", 
        "mistyrose": "#ffe4e1", 
        "moccasin": "#ffe4b5", 
        "navajowhite": "#ffdead", 
        "navy": "#000080", 
        "oldlace": "#fdf5e6", 
        "olive": "#808000", 
        "olivedrab": "#6b8e23", 
        "orange": "#ffa500", 
        "orangered": "#ff4500", 
        "orchid": "#da70d6", 
        "palegoldenrod": "#eee8aa", 
        "palegreen": "#98fb98", 
        "paleturquoise": "#afeeee", 
        "palevioletred": "#db7093", 
        "papayawhip": "#ffefd5", 
        "peachpuff": "#ffdab9", 
        "peru": "#cd853f", 
        "pink": "#ffc0cb", 
        "plum": "#dda0dd", 
        "powderblue": "#b0e0e6", 
        "purple": "#800080", 
        "red": "#ff0000", 
        "rosybrown": "#bc8f8f", 
        "royalblue": "#4169e1", 
        "saddlebrown": "#8b4513", 
        "salmon": "#fa8072", 
        "sandybrown": "#f4a460", 
        "seagreen": "#2e8b57", 
        "seashell": "#fff5ee", 
        "sienna": "#a0522d", 
        "silver": "#c0c0c0", 
        "skyblue": "#87ceeb", 
        "slateblue": "#6a5acd", 
        "slategray": "#708090", 
        "snow": "#fffafa", 
        "springgreen": "#00ff7f", 
        "steelblue": "#4682b4", 
        "tan": "#d2b48c", 
        "teal": "#008080", 
        "thistle": "#d8bfd8", 
        "tomato": "#ff6347", 
        "turquoise": "#40e0d0", 
        "violet": "#ee82ee", 
        "wheat": "#f5deb3", 
        "white": "#ffffff", 
        "whitesmoke": "#f5f5f5", 
        "yellow": "#ffff00", 
        "yellowgreen": "#9acd32"
    }

    @abc.abstractmethod
    def new_canvas(self, width, height):
        """
        Abstract method to be implemented by subclass. 

        Implemented method should return a canvas object of drawing library,
        with the given width and height.

        Args:
            width (int): The width in pixels for the new canvas object.

            height (int): The height in pixels for the new canvas object.
        
        Returns:
            new_canvas (*): A canvas object of drawing library
        """
    
    @abc.abstractmethod
    def is_canvas(self, target):
        """
        Abstract method to be implemented by subclass. 

        Implemented method should return if input is valid to draw on using the
        drawing library.

        Args:
            target (*): The object to test whether it can be drawn on.
        
        Returns:
            is_canvas (bool): whether the object can be drawn on.
        """
    
    @abc.abstractmethod
    def save(self, canvas, output):
        """
        Abstract method to be implemented by subclass. 

        Implemented method should save the given canvas to the given output 
        file.

        Args:
            canvas (*): The canvas object to save to file.
            
            output (str | None): The path to save the image to. If None, then 
                do nothing.
        
        Returns:
            None
        """

    @abc.abstractmethod
    def cache_color(self, color):
        """
        Abstract method to be implemented by subclass. 

        Implemented method should return a color object from the drawing 
        library used. Should use the BaseRenderer.color_names list for looking
        up color names.


        Args:
            color (string | tuple): A color name, a hex code, or a tuple of 
                values defining a color.
        
        Returns:
            cached_color (*): A color object for the drawing library.
        """

    @abc.abstractmethod
    def draw_background(self, canvas, style):
        """
        Abstract method to be implemented by subclass. 

        Implemented method should draw over the whole canvas using the 
        properties given in the style object. Could be a color, an image, or 
        nothing.
        

        Args:
            canvas (*): The canvas object to draw on.
        
            style (map.BackgroundStyle): A BackgroundStyle object containing 
            the style properties for the background.
        
        Returns:
            None
        """

    @abc.abstractmethod
    def draw_point(self, canvas, structure, x_values, y_values, style):
        """
        Abstract method to be implemented by subclass. 

        Implemented method should draw a point onto the given canvas using 
        the shape defined by (structure, x_values, y_values), and with a style
        defined by the given style object.

        Args:
            canvas (*): The canvas object to draw on.
            
            structure (list[ints]): The structure of the geometry. A list of
                integers counting the number of points in each subgeomtry.
            
            x_values (list[int]): List of x values of pixel coordinates for 
                each point.
            
            y_values (list[int]): List of y values of pixel coordinates for 
                each point.
            
            style (VectorLayer.FeatureStyle): A FeatureStyle containing the
                style properties for the point.
        
        Returns:
            None
        """

    @abc.abstractmethod
    def draw_line(self, canvas, structure, x_values, y_values, style):
        """
        Abstract method to be implemented by subclass. 

        Implemented method should draw a line onto the given canvas using 
        the shape defined by (structure, x_values, y_values), and with a style
        defined by the given style object.

        Args:
            canvas (*): The canvas object to draw on.
            
            structure (list[ints]): The structure of the geometry. A list of
                integers counting the number of points in each subgeomtry.
            
            x_values (list[int]): List of x values of pixel coordinates for 
                each point.
            
            y_values (list[int]): List of y values of pixel coordinates for 
                each point.
            
            style (VectorLayer.FeatureStyle): A FeatureStyle containing the
                style properties for the line.
        
        Returns:
            None
        """

    @abc.abstractmethod
    def draw_polygon(self, canvas, structure, x_values, y_values, style):
        """
        Abstract method to be implemented by subclass. 

        Implemented method should draw a polygon onto the given canvas using 
        the shape defined by (structure, x_values, y_values), and with a style
        defined by the given style object.

        Args:
            canvas (*): The canvas object to draw on.
            
            structure (list[ints]): The structure of the geometry. A list of
                integers counting the number of points in each subgeomtry.
            
            x_values (list[int]): List of x values of pixel coordinates for 
                each point.
            
            y_values (list[int]): List of y values of pixel coordinates for 
                each point.
            
            style (VectorLayer.FeatureStyle): A FeatureStyle containing the
                style properties for the polygon.
        
        Returns:
            None
        """

    @abc.abstractmethod
    def cache_image(self, image_path):
        """
        Abstract method to be implemented by subclass. 

        Implemented method should return a image object from a given path for 
        the drawing library used.


        Args:
            image_path (str): The path of the image to cache.
        
        Returns:
            cache_image (*): A image object for the drawing library.
        """

    @abc.abstractmethod
    def draw_image(self, canvas, image_cache, x, y, x_scale, y_scale, align='nw'):
        """
        Abstract method to be implemented by subclass. 

        Implemented method should draw a cached image (returned from 
        cache_image method) onto the given canvas with the given parameters.

        Args:
            canvas (*): The canvas object to draw on. Must correspond to the 
            renderer.

            image_cache (*): A cached image, returned from cache_image method.

            x (int): The pixel coordinate x value of where to place the image.
            
            y (int): The pixel coordinate y value of where to place the image.

            x_scale (int | float): The scale multiplier in the x direction.
            
            y_scale (int | float): The scale multiplier in the y direction.
        
        Optional Args:
            align='nw' (str): Where to anchor the image. Uses abbreviated
            cardinal and ordinal directions.

        Returns:
            None
        """

    @abc.abstractmethod
    def draw_text(self, canvas, text, x, y, text_style):
        """
        Abstract method to be implemented by subclass. 

        Implemented method should draw a given string onto the given canvas, 
        using the given text_style object.

        Args:
            canvas (*): The canvas object to draw on. Must correspond to the 
            renderer.

            text (str): The text string to draw.

            text_style (TextStyle): The TextStyle object containing style
            infomation.
    
        Returns:
            None
        """