"""
Author: Ben Knisley [benknisley@gmail.com]
Date: 2 September, 2021
"""
from .base_layer import BaseLayer
from .base_style import Style



def build_textline_style(feature, parent_style=None):
    """
    Returns a configured Style Object for the given geometry type. If a parent 
    style object is given it makes the new style a child style.
    """
    style = Style(feature)

    style.add_property('color', 'black')
    style.add_property('font_size', 12)
    style.add_property('typeface', None)
    style.add_property('bold', False)
    style.add_property('italic', False)

    if parent_style:
        parent_style.add_child_style(style)
    
    return style

class TextLine:
    """
    Class to hold info about a line of text.
    """
    def __init__(self, parent, text):
        """
        """

        self.parent = parent

        ## Setup variable to hold the text value
        self.text = text

        ## Setup style
        self.style = build_textline_style(self, self.parent.style)

    def __repr__(self):
        """ Returns self.text as objects' string representation """
        return self.text

    def get_height(self):
        """ Returns the height of the text line in pixels. """
        return self.style['font_size'] #/ 1.2

    def get_width(self):
        """ Returns the width of the text line in pixels. """
        return (self.style['font_size'] * 0.5) * len(self.text)

class TextBlock:
    def __init__(self, parent, init_string, x_place, y_place):
        """
        Class to hold lines of text.
        """
        ## Save reference to parent TextLayer
        self.layer = parent

        ## Setup style
        self.style = build_textline_style(self, self.layer.style)

        ## Set text align
        self.align = 'left'
        self.padding = 10 ## Px

        ## Create a TextLine instance for each line
        init_string = init_string.replace('\\', '\n')
        text_lines = [TextLine(self, w.strip()) for w in init_string.split('\n')]
        self.text_lines = text_lines if text_lines else []

        ## Placement vars
        self.x = x_place
        self.y = y_place

    def __repr__(self):
        retn_text = self.text_lines[0].text if self.text_lines else ""
        for line in self.text_lines[1:]:
            retn_text += '\n'
            retn_text += line.text

        return retn_text

    def __getitem__(self, key):
        """ Returns"""
        return self.text_lines[key]

    def set_alignment(self, new_alignment):
        self.align = new_alignment

    def get_width(self):
        return max([l.get_width() for l in self.text_lines])

    def get_height(self):
        return sum([l.get_height() for l in self.text_lines])

    def alignment_offset(self, line_width):
        if self.align == 'left':
            return 0
        elif self.align == 'center':
            return (self.get_width() - line_width)/2.0
        elif self.align == 'right':
            return self.get_width() - line_width

    def placement(self, axis, input):

        if axis == 'x':
            if input == 'c':
                map_width = self.layer.map.get_size()[0]
                block_width = max([l.get_width() for l in self.text_lines])
                return (map_width - block_width) / 2
            elif input == 'l':
                return self.padding
            elif input == 'r':
                return (self.layer.map.get_size()[0] - self.get_width()) - self.padding
            else:
                return input

        if axis == 'y':
            if input == 'c':
                map_height = self.layer.map.get_size()[1]
                block_height = self.get_height()
                return (map_height - block_height) / 2
            elif input == 't':
                return self.padding
            elif input == 'b':
                return (self.layer.map.get_size()[1] - self.get_height()) - self.padding
            return input

    def add_line(self, text, position=-1):
        new_text_line = TextLine(self, text)
        if position == -1:
            self.text_lines.append(new_text_line)
        else:
            self.text_lines.insert(position, new_text_line)
        return new_text_line

    def render(self, renderer, canvas):
        """
        """
        x = self.placement('x', self.x)
        y = self.placement('y', self.y)

        y_index = y
        for text_line in self.text_lines:
            line_x_off = self.alignment_offset(text_line.get_width())
            y_index += text_line.get_height()
            renderer.draw_text(canvas, text_line.text, x + line_x_off, y_index, text_line.style)


class TextLayer(BaseLayer):
    """
    A class and a MapLayer to hold text blocks.
    """
    def __init__(self):
        ## Subclass Baselayer
        BaseLayer.__init__(self)

        ## Setup layer name
        self.name = "Static Text Layer"

        ## Setup style
        self.style = build_textline_style(self)

        ## Create a list to hold text elements
        self.text_elements = []

    def __getitem__(self, key):
        """ Returns"""
        return self.text_elements[key]
        
    def __repr__(self):
        '''
        ...

        Args:
            None
    
        Returns:
            repr_str (str): A string representation of the LabelLayer.
        '''
        num_blocks = len(self.text_elements)
        return f"Label Layer Object, containing {num_blocks} blocks"

    def activate(self):
        '''
        Abstract method to be implemented by child layer. 
        Contains any code required by a layer to fully activate it with the new
        map object. Called by BaseLayer._activate after it adds the parent map 
        object to the layer.

        Args:
            None
    
        Returns:
            None
        '''
    
    def deactivate(self):
        ''' 
        Abstract method to be implemented by child layer. 
        Contains any code required by a layer to fully deactivate and reset it.
        Called by BaseLayer._deactivate which actually removes the map object 
        from the layer.

        Args:
            None
    
        Returns:
            None
        '''

    def get_extent(self):
        ''' 
        Abstract method to be implemented by child layer. 
        Returns the extent of the data in projection coordinates.
        
        Args:
        None
    
        Returns:
            min_x (float): The minimum x projection coordinate of the data.
            min_y (float): The minimum y projection coordinate of the data.
            max_x (float): The maximum x projection coordinate of the data.
            max_y (float): The maximum y projection coordinate of the data.
        '''
        return None

    def add_text_block(self, input_text, x_place, y_place):
        """
        """
        new_text_block = TextBlock(self, input_text, x_place, y_place)
        self.text_elements.append(new_text_block)
        return new_text_block

    def render(self, renderer, canvas):
        ''' 
        Draws the text layer onto a canvas using the renderer.

        Args:
        renderer (BaseRenderer): The renderer to use to draw on the canvas.

        canvas (Unknown): The canvas to draw on.
    
        Returns:
            None
        '''

        for text_element in self.text_elements:
            text_element.render(renderer, canvas)
