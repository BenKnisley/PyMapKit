"""
Author: Ben Knisley [benknisley@gmail.com]
Date: 2 September, 2021
"""
from .base_layer import BaseLayer
from .base_style import BaseStyle


class TextLine:
    """
    Class to hold info about a line of text.
    """
    def __init__(self, text):
        """
        """
        ## Setup variable to hold the text value
        self.text = text

        ## Setup text line style profile
        self.style = TextLineStyle(self)


    def __repr__(self):
        return self.text

    def get_height(self):
        """ Returns the height of the text line in pixels. """
        return self.style['font_size'] #/ 1.2

    def get_width(self):
        """ Returns the width of the text line in pixels. """
        return (self.style['font_size'] * 0.5) * len(self.text)

class TextLineStyle(BaseStyle):
    def __init__(self, parent_feature):
        BaseStyle.__init__(self, parent_feature)

        ## Setup style
        self.add_property('font_size', 12)
        self.add_property('typeface', None)
        self.add_property('color', 'black')
        self.add_property('bold', False)
        self.add_property('italic', False)
        

class TextBlock:
    def __init__(self, parent, init_string, x_place, y_place):
        """
        Class to hold lines of text.
        """
        ## Save reference to parent TextLayer
        self.layer = parent

        ## Set text align
        self.align = 'left'
        self.padding = 10 ##Px

        ## Create a TextLine instance for each line
        text_lines = [TextLine(w.strip()) for w in init_string.split('\\')]
        self.text_lines = text_lines if text_lines else []


        self.style = TextBlockStyle(self)
        self.style.add_property('font_size', 12)
        self.style.add_property('typeface', None)
        self.style.add_property('color', 'black')
        self.style.add_property('bold', False)
        self.style.add_property('italic', False)

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

class TextBlockStyle(BaseStyle):
    def __init__(self, parent_feature):
        BaseStyle.__init__(self, parent_feature)
        self.layer = parent_feature

    def create_domain_mode_etters(self, domain_name):

        ## Add domain setter to feature
        def set_display_template(self, new_value):
            self.style.set_mode(new_value, domain_name)
            self.style.clear_cache()
            
            for f in self:
                f.style.set_mode(new_value, domain_name)
                f.style.clear_cache()
        
        if domain_name:
            setter_name = 'set_' + domain_name + '_display'
            getter_name = 'get_' + domain_name + '_display'
        else:
            setter_name = 'set_display'
            getter_name = 'get_display'
        
        bound_setter = set_display_template.__get__(self.feature, type(self.feature))
        self.feature.__dict__[setter_name] = bound_setter

        ## Add domain getter to feature
        def get_display_template(self):
            return self.style.current_modes[domain_name]

        ## Link, and bind set_display as a named method of the parent feature
        bound_getter = get_display_template.__get__(self.feature, type(self.feature))
        self.feature.__dict__[getter_name] = bound_getter

        ## Bind a getter to self too
        def get_display_template(self):
            return self.current_modes[domain_name]

        ## Link, and bind set_display as a named method of the parent feature
        bound_getter = get_display_template.__get__(self, type(self))
        self.__dict__[getter_name] = bound_getter

    def create_property_etters(self, property_name):

        ## Define [g][s]et_display templates
        def set_property_template(self, new_value):
            for f in self:
                if property_name in f.style.managed_properties:
                    f.style.managed_properties[property_name] = new_value
                f.style.clear_cache()

        ## Link, and bind set_display as a named method of the parent feature
        bound_setter = set_property_template.__get__(self.feature, type(self.feature))
        self.feature.__dict__['set_'+property_name] = bound_setter

        def get_property_template(self):
            return self.style.managed_properties[property_name]

        ## Link, and bind set_display as a named method of the parent feature
        bound_getter = get_property_template.__get__(self.feature, type(self.feature))
        self.feature.__dict__['get_'+property_name] = bound_getter

    def clear_cache(self):
        for f in self.layer:
            f.style.cached_renderer_fn = None




class StaticTextLayer(BaseLayer):
    """
    A class and a MapLayer to hold text blocks.
    """
    def __init__(self):
        ## Subclass Baselayer
        BaseLayer.__init__(self)

        ## Setup layer name
        self.name = "Static Text Layer"

        ## Create a list to hold text elements
        self.text_elements = []

    def add_text_block(self, input_text, x_place, y_place):
        """
        """
        self.text_elements.append(TextBlock(self, input_text, x_place, y_place))

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
        return "Label Layer Object"

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

    def render(self, renderer, canvas):
        ''' 
        Abstract method to be implemented by child layer. 
        Draws the layer onto a canvas using the renderer.

        Args:
        renderer (BaseRenderer): The renderer to use to draw on the canvas.

        canvas (Unknown): The canvas to draw on.
    
        Returns:
            None
        '''

        for text_element in self.text_elements:
            text_element.render(renderer, canvas)