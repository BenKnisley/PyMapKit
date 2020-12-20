"""
Project: PyMapKit
Title: Text Layer
Function: Provides a class that can display static text.
Author: Ben Knisley [benknisley@gmail.com]
Created: 16 June, 2020
"""

class _text_line:
    """ """
    ## Class Defaults
    font = ""
    color = 'black'
    size = 10
    bold = False
    italic = False

    def __init__(self, text_string):
        self.text = text_string
        ## Copy default values over from class Defaults
        self.font = _text_line.font
        self.size = _text_line.size
        self.color = _text_line.color
        self.bold = _text_line.bold
        self.italic = _text_line.italic
    
    def line_height(self):
        return self.size * 1.334 ## Pt to px convert
    
    def line_width(self):
        return (self.size * 0.6) * len(self.text)
    
    def get_text(self):
        return self.text
    
    def set_text(self, text):
        self.text = text

    def get_color(self):
        return self.color

    def set_color(self, color):
        self.color = color
    
    def get_font(self):
        if self.font == "":
            return "DEFAULT SYSTEM FONT"
        else:
            return self.font

    def set_font(self, font):
        self.font = font

    def get_font_size(self):
        return self.size

    def set_font_size(self, font_size):
        self.size = font_size
    
    def is_bold(self):
        return self.bold

    def set_bold(self, is_bold):
        self.bold = is_bold
    
    def is_italic(self):
        return self.is_italic

    def set_italic(self, is_italic):
        self.italic = is_italic

class _text_feature:
    """ """
    def __init__(self, text_string, x_pos, y_pos):
        self.lines = []
        self.x_pos = x_pos
        self.y_pos = y_pos

        for line_string in text_string.split('\\'):
            line_string = line_string.strip()
            new_line = _text_line(line_string)
            self.lines.append(new_line)
    
    def __getitem__(self, index):
        return self.lines[index]

    def __iter__(self):
        ## Create index for iteration and return self
        self._iter_indx = 0
        return self

    def __next__(self):
        if self._iter_indx == len(self.lines):
            raise StopIteration

        line = self.lines[self._iter_indx]
        self._iter_indx += 1
        return line

    def _activate(self, layer):
        self.layer = layer
    
    def _deactivate(self):
        self.layer = None
    
    def add_line(self, text):
        new_line = _text_line(text)
        self.lines.append(new_line)
        return new_line

    def set_color(self, color):
        for line in self:
            line.color = color
    
    def set_font(self, font):
        for line in self:
            line.font = font

    def set_font_size(self, font_size):
        for line in self:
            line.size = font_size
    
    def set_bold(self, is_bold):
        for line in self:
            line.bold = is_bold
    
    def set_italic(self, is_italic):
        for line in self:
            line.italic = is_italic
    
    def draw(self, renderer, cr):
        x_margin = 5
        y_margin = 5
        
        ## Draw each line in feature
        for i, line in enumerate(self.lines):
            ## Find X position
            if self.x_pos in ('l', 'left'):
                x_pos = x_margin
            elif self.x_pos in ('c', 'center', 'centre'):
                x_pos = (self.layer.parent.width / 2) - (self.lines[i].line_width() / 2)
            elif  self.x_pos in ('r', 'right'):
                x_pos = self.layer.parent.width - x_margin
            else:
                x_pos = self.x_pos

            ## Find Y postion
            if self.y_pos in ('t', 'top'):
                y_pos = y_margin
                y_pos += sum(map(lambda line: line.line_height(), self.lines[:i]))
                y_pos += line.line_height()

            elif self.y_pos in ('c', 'center', 'centre'):
                y_pos = self.layer.parent.height / 2
                y_pos += sum(map(lambda line: line.line_height(), self.lines[:i]))

            elif  self.y_pos in ('b', 'bottom'):
                y_pos = self.layer.parent.height #- y_margin
                y_pos -= sum(map(lambda line: line.line_height(), self.lines[i:]))
                #y_pos += line.line_height()

            else:
                y_pos = self.y_pos
                y_pos += sum(map(lambda line: line.line_height(), self.lines[:i]))

            ## Draw with renderer
            renderer.draw_text(cr, line, x_pos, y_pos)

class TextLayer:
    """ """
    def __init__(self, text=""):
        """ """
        self.parent = None
        self.features = []

        if text: ## If new text is given
            self.add_text(text, 'center', 'top')

    def __getitem__(self, index):
        return self.features[index]

    def __iter__(self):
        ## Create index for iteration and return self
        self._iter_indx = 0
        return self

    def __next__(self):
        if self._iter_indx == len(self.features):
            raise StopIteration

        line = self.features[self._iter_indx]
        self._iter_indx += 1
        return line

    def add_text(self, text, x_pos, y_pos):
        new_feature = _text_feature(text, x_pos, y_pos)
        self.features.append(new_feature)
        new_feature._activate(self)        
        return new_feature

    def _activate(self, new_parent_map):
        """ Function called when layer is added to Map Object."""
        self.parent = new_parent_map

    def _deactivate(self):
        """ Function called when layer is removed from a Map Object """
        self.parent = None

    def set_color(self, color):
        _text_line.color = color
        for feature in self:
            for line in feature:
                line.color = color
    
    def set_font(self, font):
        _text_line.font = font
        for feature in self:
            for line in feature:
                line.font = font


    def set_font_size(self, font_size):
        _text_line.size = font_size
        for feature in self:
            for line in feature:
                line.font_size = font_size

    
    def set_bold(self, is_bold):
        _text_line.bold = is_bold
        for feature in self:
            for line in feature:
                line.bold = is_bold

    
    def set_italic(self, is_italic):
        _text_line.italic = is_italic
        for feature in self:
            for line in feature:
                line.italic = is_italic


    def draw(self, renderer, cr):
        """ """
        for feature in self.features:
            feature.draw(renderer, cr)

