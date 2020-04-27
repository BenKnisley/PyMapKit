#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date:
"""
import math #! TODO: Replace math.isclose with pytest.approx
import pytest
import pyproj
import MapEngine

def _color_converter(input_color):
    """ Converts different color formats into single format.

    Inputs:
        - (float, float, float) - A tuple of three floats between 0.0 and 1.0
            representing red, green, & blue values respectively.

        - (int, int, int) - A tuple of three ints between 0 and 1
            representing red, green, & blue values respectively.

        - "#0F0F0F" - A html color hex string.

        - "colorname" - A html color name.

    Returns:
        - (float, float, float) - A tuple of three floats between 0.0 and 1.0
            representing red, green, & blue values respectively.

    """
    ## Two tuple types, 0-1 or 0-256
    if isinstance(input_color, tuple):

        ## If float tuple, input same as output
        if isinstance(input_color[0], float):
            return input_color

        if isinstance(input_color[0], int):
            R = input_color[3] / 255.0
            G = input_color[5] / 255.0
            B = input_color[7] / 255.0
            return (R,G,B)

    ## Two types of color strings: Html color names and hex
    if isinstance(input_color, str):
        ## Define color dictionary, with html color names defined
        color_dict = {"aliceblue": "#f0f8ff", "antiquewhite": "#faebd7", "aqua": "#00ffff", "aquamarine": "#7fffd4", "azure": "#f0ffff", "beige": "#f5f5dc", "bisque": "#ffe4c4", "black": "#000000", "blanchedalmond": "#ffebcd", "blue": "#0000ff", "blueviolet": "#8a2be2", "brown": "#a52a2a", "burlywood": "#deb887", "cadetblue": "#5f9ea0", "chartreuse": "#7fff00", "chocolate": "#d2691e", "coral": "#ff7f50", "cornflowerblue": "#6495ed", "cornsilk": "#fff8dc", "crimson": "#dc143c", "cyan": "#00ffff", "darkblue": "#00008b", "darkcyan": "#008b8b", "darkgoldenrod": "#b8860b", "darkgray": "#a9a9a9", "darkgreen": "#006400", "darkkhaki": "#bdb76b", "darkmagenta": "#8b008b", "darkolivegreen": "#556b2f", "darkorange": "#ff8c00", "darkorchid": "#9932cc", "darkred": "#8b0000", "darksalmon": "#e9967a", "darkseagreen": "#8fbc8f", "darkslateblue": "#483d8b", "darkslategray": "#2f4f4f", "darkturquoise": "#00ced1", "darkviolet": "#9400d3", "deeppink": "#ff1493", "deepskyblue": "#00bfff", "dimgray": "#696969", "dodgerblue": "#1e90ff", "firebrick": "#b22222", "floralwhite": "#fffaf0", "forestgreen": "#228b22", "fuchsia": "#ff00ff", "gainsboro": "#dcdcdc", "ghostwhite": "#f8f8ff", "gold": "#ffd700", "goldenrod": "#daa520", "gray": "#808080", "green": "#008000", "greenyellow": "#adff2f", "honeydew": "#f0fff0", "hotpink": "#ff69b4", "indianred": "#cd5c5c", "indigo": "#4b0082", "ivory": "#fffff0", "khaki": "#f0e68c", "lavender": "#e6e6fa", "lavenderblush": "#fff0f5", "lawngreen": "#7cfc00", "lemonchiffon": "#fffacd", "lightblue": "#add8e6", "lightcoral": "#f08080", "lightcyan": "#e0ffff", "lightgoldenrodyellow": "#fafad2", "lightgray": "#d3d3d3", "lightgreen": "#90ee90", "lightpink": "#ffb6c1", "lightsalmon": "#ffa07a", "lightseagreen": "#20b2aa", "lightskyblue": "#87cefa", "lightslategray": "#778899", "lightsteelblue": "#b0c4de", "lightyellow": "#ffffe0", "lime": "#00ff00", "limegreen": "#32cd32", "linen": "#faf0e6", "magenta": "#ff00ff", "maroon": "#800000", "mediumaquamarine": "#66cdaa", "mediumblue": "#0000cd", "mediumorchid": "#ba55d3", "mediumpurple": "#9370d8", "mediumseagreen": "#3cb371", "mediumslateblue": "#7b68ee", "mediumspringgreen": "#00fa9a", "mediumturquoise": "#48d1cc", "mediumvioletred": "#c71585", "midnightblue": "#191970", "mintcream": "#f5fffa", "mistyrose": "#ffe4e1", "moccasin": "#ffe4b5", "navajowhite": "#ffdead", "navy": "#000080", "oldlace": "#fdf5e6", "olive": "#808000", "olivedrab": "#6b8e23", "orange": "#ffa500", "orangered": "#ff4500", "orchid": "#da70d6", "palegoldenrod": "#eee8aa", "palegreen": "#98fb98", "paleturquoise": "#afeeee", "palevioletred": "#db7093", "papayawhip": "#ffefd5", "peachpuff": "#ffdab9", "peru": "#cd853f", "pink": "#ffc0cb", "plum": "#dda0dd", "powderblue": "#b0e0e6", "purple": "#800080", "red": "#ff0000", "rosybrown": "#bc8f8f", "royalblue": "#4169e1", "saddlebrown": "#8b4513", "salmon": "#fa8072", "sandybrown": "#f4a460", "seagreen": "#2e8b57", "seashell": "#fff5ee", "sienna": "#a0522d", "silver": "#c0c0c0", "skyblue": "#87ceeb", "slateblue": "#6a5acd", "slategray": "#708090", "snow": "#fffafa", "springgreen": "#00ff7f", "steelblue": "#4682b4", "tan": "#d2b48c", "teal": "#008080", "thistle": "#d8bfd8", "tomato": "#ff6347", "turquoise": "#40e0d0", "violet": "#ee82ee", "wheat": "#f5deb3", "white": "#ffffff", "whitesmoke": "#f5f5f5", "yellow": "#ffff00", "yellowgreen": "#9acd32"}

        if input_color.lower() in color_dict:
            input_color = color_dict[input_color.lower()]


        if '#' in input_color and len(input_color) == 7:
            ## Hex string color
            R = int(input_color[1:3], 16) / 255.0
            G = int(input_color[3:5], 16) / 255.0
            B = int(input_color[5:7], 16) / 255.0
            return (R,G,B)

def test_init():
    """ Test initiation of MapEngine Object  """
    m = MapEngine.MapEngine()
    assert isinstance(m, MapEngine.MapEngine), "MapEngine object was not created."

def test_init_defaults(): 
    m = MapEngine.MapEngine()
    assert m._WGS84 == pyproj.Proj("EPSG:4326"), "_WGS84 projection not EPSG:4326"
    assert isinstance(m._layer_list, list), "_layer_list not type list"
    assert len(m._layer_list) == 0, "_layer_list already has content"
    assert m._projection == pyproj.Proj("EPSG:4326"), "Default projection not EPSG:4326" 
    assert m._scale == 50000.0, "Default scale is not 50000.0"
    assert math.isclose(m._proj_scale, 0.452202225, rel_tol=1e-9, abs_tol=0.0), "_proj_scale is not correct"
    assert m.height == 500, "Default height is not 500 pixels"
    assert m.width == 500, "Default width is not 500 pixels"
    assert m.longitude == 0.0, "Default longitude is not 0 degrees"
    assert m.latitude == 0.0, "Default latitude is not 0 degrees"
    assert m._projx == 0.0, "Default _proj_x is not correct"
    assert m._projy == 0.0, "Default _proj_y is not correct"
    assert m._background_color == _color_converter('#0C0C0C'), "Default background color not correct"

def test_init_args():
    m = MapEngine.MapEngine( projection="EPSG:3735", scale=500, longitude=-82.1, latitude=40.0, width=600, height=500)
    assert m._WGS84 == pyproj.Proj("EPSG:4326")
    assert m._projection == pyproj.Proj("EPSG:3735")
    assert m._scale == 500, "scale did not set correctly"
    assert m.width == 600, "width did not set correctly"
    assert m.height == 500, "height did not set correctly"
    assert math.isclose(m.longitude, -82.1, rel_tol=1e-9, abs_tol=0.0), "longitude did not set correctly"
    assert math.isclose(m.latitude, 40.0, rel_tol=1e-9, abs_tol=0.0),  "latitude did not set correctly"

def test_add_layer():
    """ Test basic function of add_layer method """
    m = MapEngine.MapEngine()
    
    v1 = MapEngine.VectorLayer.VectorLayer(None, [], [])
    v2 = MapEngine.VectorLayer.VectorLayer(None, [], [])
    v3 = MapEngine.VectorLayer.VectorLayer(None, [], [])
    
    m.add_layer(v1)
    assert len(m._layer_list) == 1
    assert m._layer_list[0] == v1

    m.add_layer(v2)
    assert len(m._layer_list) == 2
    assert m._layer_list[0] == v2

    
    m.add_layer(v3, 1)
    assert len(m._layer_list) == 3
    assert m._layer_list[0] == v2
    assert m._layer_list[1] == v3
    assert m._layer_list[2] == v1

def test_remove_layer():
    """ Test basic function of remove_layer method """
    m = MapEngine.MapEngine()
    
    v1 = MapEngine.VectorLayer.VectorLayer(None, [], [])
    v2 = MapEngine.VectorLayer.VectorLayer(None, [], [])
    v3 = MapEngine.VectorLayer.VectorLayer(None, [], [])
    
    m.add_layer(v1)
    m.add_layer(v2)
    m.add_layer(v3)
    
    with pytest.raises(Exception):
        m.remove_layer(3)

    m.remove_layer(0)
    assert len(m._layer_list) == 2
    assert m._layer_list[0] == v2
    assert m._layer_list[1] == v1

    m.remove_layer(1)
    assert len(m._layer_list) == 1
    assert m._layer_list[0] == v2

    m.remove_layer(0)
    assert len(m._layer_list) == 0

    with pytest.raises(Exception):
        m.remove_layer(0)

def test_get_layer():
    """ Test basic function of get_layer method """
    m = MapEngine.MapEngine()
    v1 = MapEngine.VectorLayer.VectorLayer(None, [], [])
    v2 = MapEngine.VectorLayer.VectorLayer(None, [], [])
    v3 = MapEngine.VectorLayer.VectorLayer(None, [], [])
    m.add_layer(v1)
    m.add_layer(v2)
    m.add_layer(v3)
    
    with pytest.raises(Exception):
        m.get_layer(3)
    
    assert m.get_layer(0) == v3
    assert len(m._layer_list) == 3
    
    assert m.get_layer(2) == v1
    assert len(m._layer_list) == 3

    assert m.get_layer(1) == v2
    assert len(m._layer_list) == 3

def test_get_projection():
    """ Test basic function of get_projection method """
    m = MapEngine.MapEngine()

    ## Test default 
    assert m.get_projection() == pyproj.Proj("EPSG:4326").srs

    ## Set new and test get projection  
    m.set_projection("EPSG:3735")
    assert m.get_projection() == pyproj.Proj("EPSG:3735").srs

def test_set_projection():
    """ Test basic function of set_projection method """
    m = MapEngine.MapEngine()

    ## Set new projection from string
    m.set_projection("EPSG:3735")
    assert m.get_projection() == pyproj.Proj("EPSG:3735").srs

    ## Change projection again
    p = pyproj.Proj("EPSG:4326")
    m.set_projection(p)
    assert m.get_projection() == pyproj.Proj("EPSG:4326").srs

    ## Set Projection from proj string
    m.set_projection("+proj=longlat +datum=WGS84 +no_defs")
    assert m.get_projection() == pyproj.Proj("+proj=longlat +datum=WGS84 +no_defs").srs

    ## Set Projection from proj obj
    p = pyproj.Proj("EPSG:3735")
    m.set_projection(p)
    assert m.get_projection() == pyproj.Proj("EPSG:3735").srs

def test_get_proj_coordinate():
    """ Test retrieval of projection coords """
    m = MapEngine.MapEngine()

    ## Test default 
    assert m.get_proj_coordinate()[0] == 0
    assert m.get_proj_coordinate()[1] == 0

    ## Test after change
    m.set_proj_coordinate(18853, -45670)
    assert m.get_proj_coordinate()[0] == 18853
    assert m.get_proj_coordinate()[1] == -45670

def test_set_proj_coordinate():
    """ Test retrieval of projection coords """
    m = MapEngine.MapEngine()

    m.set_proj_coordinate(18853, -45670)
    assert m.get_proj_coordinate()[0] == 18853
    assert m.get_proj_coordinate()[1] == -45670
    
    m.set_proj_coordinate(180, 90)
    assert m.get_proj_coordinate()[0] == 180
    assert m.get_proj_coordinate()[1] == 90


def test_set_location():
    """ Test setting location from geo coord"""
    m = MapEngine.MapEngine()

    m.set_location(40.0, -83.0)
    lat, lon = m.get_location()
    assert lat == pytest.approx(40.0, rel=1e-3)
    assert lon == pytest.approx(-83.0, rel=1e-3)

    m.set_location(-10.1, 43.4)
    lat, lon = m.get_location()
    assert lat == pytest.approx(-10.1, rel=1e-3) 
    assert lon == pytest.approx(43.4, rel=1e-3) 


def test_get_location():
    """ Test getting location from geo coord"""
    m = MapEngine.MapEngine()

    m.set_location(40.0, -83.0)
    lat, lon = m.get_location()
    assert lat == pytest.approx(40.0, rel=1e-3)
    assert lon == pytest.approx(-83.0, rel=1e-3)

    m.set_location(-10.1, 43.4)
    lat, lon = m.get_location()
    assert lat == pytest.approx(-10.1, rel=1e-3) 
    assert lon == pytest.approx(43.4, rel=1e-3) 