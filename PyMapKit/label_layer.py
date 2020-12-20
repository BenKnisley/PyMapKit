"""
Project: PyMapKit
Title: Text Layer
Function: Provides a class that can display static text.
Author: Ben Knisley [benknisley@gmail.com]
Created: 23 September, 2020
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



class LabelFeature:
    def __init__(self, parent, text, x, y, proj=True):
        self.parent = parent
        self.text = _text_line(text)
        
        if parent.parent == None:
            self.proj_x = None
            self.proj_y = None
        else:
            if proj:
                self.proj_x, self.proj_y = x, y
                self.geo_x = None
                self.geo_y = None
            else:
                self.proj_x, self.proj_y = parent.parent.geo2proj(geo_x, geo_y)
    
    def _activate(self, new_parent):
        self.parent = new_parent

        #self.proj_x, self.proj_y = self.parent.parent.geo2proj(self.geo_x, self.geo_y)
    
    def draw(self, renderer, cr):
        x, y = self.parent.parent.proj2pix(self.proj_x, self.proj_y)

        #x -= (int(self.text.line_width()) / 2.0)
        #y -= (int(self.text.line_height()) / 2.0)

        renderer.draw_text(cr, self.text, x, y, True)





class LabelLayer:
    """ """
    def __init__(self):
        """ """
        self.parent = None
        self.features = []

    def _activate(self, parent):
        self.parent = parent

        for feature in self.features:
            feature._activate(self)

    def add_label(self, text, geo_x, geo_y):
        new_feature = LabelFeature(self, text, geo_x, geo_y)
        self.features.append(new_feature)

    def draw(self, renderer, cr):
        for feature in self.features:
            feature.draw(renderer, cr)

