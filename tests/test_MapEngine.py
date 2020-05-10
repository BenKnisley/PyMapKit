#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date:
"""
import math #! TODO: Replace math.isclose with pytest.approx
import pytest
import numpy as np
from unittest.mock import MagicMock
import pyproj
import MapEngine

## Set up empty class for mocks
class bare_class:
    pass

## Create a mock_layer class
class mock_layer:
    def __init__(self):
        ## Create a mock draw function
        self.draw = MagicMock()
        self._activate = MagicMock()


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
    assert m._background_color == '#0C0C0C', "Default background color not correct"

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

#! TODO: Merge getters and setters into same test
def test_longitude_getter():
    """ Test the longitude setter property"""
    m = MapEngine.MapEngine()

    m.set_location(40.0, -83.1)
    assert m.longitude == pytest.approx(-83.1, rel=1e-3)

    m.set_location(-12.2, -10.3)
    assert m.longitude == pytest.approx(-10.3, rel=1e-3)

def test_longitude_setter():
    """ Test the longitude setter property"""
    m = MapEngine.MapEngine()

    m.longitude = 21.1
    assert m.longitude == pytest.approx(21.1, rel=1e-3)

    m.longitude = -0.1
    assert m.longitude == pytest.approx(-0.1, rel=1e-3)

def test_latitude_getter():
    """ Test the latitude setter property"""
    m = MapEngine.MapEngine()

    m.set_location(40.0, -83.1)
    assert m.latitude == pytest.approx(40.0, rel=1e-3)

    m.set_location(-12.2, -10.3)
    assert m.latitude == pytest.approx(-12.2, rel=1e-3)

def test_latitude_setter():
    """ Test the latitude setter property"""
    m = MapEngine.MapEngine()

    m.latitude = -102.1
    assert m.latitude == pytest.approx(-102.1, rel=1e-3)

    m.latitude = 23.12
    assert m.latitude == pytest.approx(23.12, rel=1e-3)

def test_set_scale():
    """ Test the set_scale method """
    m = MapEngine.MapEngine()

    ## Set projection to one with degrees as units
    m.set_projection("EPSG:4326")

    ## Set Scale to 30 pix per meter
    m.set_scale(30)
    assert m._scale == 30
    assert m._proj_scale == pytest.approx(0.000271321, rel=1e-5)

    ## Set Scale to 30 pix per meter
    m.set_scale(1)
    assert m._scale == 1
    assert m._proj_scale == pytest.approx(0.000009044, rel=1e-5)

    ## Set projection to one with feet as units
    m.set_projection("EPSG:3735")

    ## Set Scale to 30 pix per meter
    m.set_scale(30)
    assert m._scale == 30
    assert m._proj_scale == pytest.approx(98.4252, rel=1e-5)

    ## Set Scale to 30 pix per meter
    m.set_scale(1)
    assert m._scale == 1
    assert m._proj_scale == pytest.approx(3.28084, rel=1e-5)
    
    ## Set projection to one with meters as units
    m.set_projection("EPSG:32122")

    ## Set Scale to 30 pix per meter
    m.set_scale(30)
    assert m._scale == 30
    assert m._proj_scale == pytest.approx(30, rel=1e-5)

    ## Set Scale to 30 pix per meter
    m.set_scale(1)
    assert m._scale == 1
    assert m._proj_scale == pytest.approx(1, rel=1e-5)

def test_get_scale():
    """ Test the get scale method"""
    m = MapEngine.MapEngine()

    m.set_scale(30)
    assert m.get_scale() == 30
    
    m.set_scale(1)
    assert m.get_scale() == 1

    m.set_scale(0.00005)
    assert m.get_scale() == 0.00005

    m.set_scale(50000.01)
    assert m.get_scale() == 50000.01

def test_set_size():
    """ Test the set_size method """
    m = MapEngine.MapEngine()

    m.set_size(250, 250)
    assert m._width == 250
    assert m._height == 250

    m.set_size(1920, 1080)
    assert m._width == 1920
    assert m._height == 1080

    m.set_size(800, 600)
    assert m._width == 800
    assert m._height == 600

def test_get_size():
    """ Test the basic function of the get_size method """
    m = MapEngine.MapEngine()

    m._width = 250
    m._height = 250
    assert m.get_size() == (250, 250)

    m._width = 1920
    m._height = 1080
    assert m.get_size() == (1920, 1080)

    m._width = 800
    m._height = 600
    assert m.get_size() == (800, 600)

def test_width_property():
    """ Test the basic function of width property """
    m = MapEngine.MapEngine()

    ## Test getter
    m._width = 250
    m._height = 250
    assert m.width == 250

    m._width = 1920
    m._height = 1080
    assert m.width == 1920
    
    m._width = 800
    m._height = 600
    assert m.width == 800

    ## Test Setter
    m.width = 300
    assert m._width == 300

    m.width = 1
    assert m._width == 1

    m.width = 250
    assert m._width == 250

def test_height_property():
    """ Test the basic function of height property """
    m = MapEngine.MapEngine()

    ## Test getter
    m._width = 250
    m._height = 250
    assert m.height == 250

    m._width = 1920
    m._height = 1080
    assert m.height == 1080
    
    m._width = 800
    m._height = 600
    assert m.height == 600

    ## Test Setter
    m.height = 300
    assert m._height == 300

    m.height = 1
    assert m._height == 1

    m.height = 250
    assert m._height == 250

def test_get_canvas_center():
    """ Test the basic function of get_canvas_center method """
    m = MapEngine.MapEngine()

    m.set_size(500,500)
    rtrn = m.get_canvas_center()
    assert rtrn[0] == 250
    assert rtrn[1] == 250

    m.set_size(8000, 6000)
    rtrn = m.get_canvas_center()
    assert rtrn[0] == 4000
    assert rtrn[1] == 3000

    m.set_size(1243, 3241)
    rtrn = m.get_canvas_center()
    assert rtrn[0] == 621
    assert rtrn[1] == 1620

def test_set_background_color():
    """ Test basic function of set_background_color method """
    m = MapEngine.MapEngine()

    m.set_background_color('red')
    assert m._background_color == 'red'

    m.set_background_color('#ffffff')
    assert m._background_color == '#ffffff'

    m.set_background_color((132, 34, 55))
    assert m._background_color == (132, 34, 55)

    m.set_background_color((0.1, 0.23, 0.55))
    assert m._background_color == (0.1, 0.23, 0.55)

def test_render():
    """ Tests basic function of the render method """
    ## Create a mock canvas
    canvas = object()
    
    ## Create mock renderer
    renderer = bare_class()
    renderer.draw_background = MagicMock()

    ## Run test
    m = MapEngine.MapEngine()
    m.add_layer(mock_layer())
    m.add_layer(mock_layer())
    m.add_layer(mock_layer())
    m.render(renderer, canvas)

    ## Assert draw background was called once and correct
    renderer.draw_background.assert_called_once_with(canvas, m._background_color)

    ## Check that all layers were run correct
    for l in m._layer_list:
        l.draw.assert_called_once_with(renderer, canvas)

def test_geo2proj():
    """ Tests basic function of the geo2proj method """
    ## Create new MapEngine object for test
    m = MapEngine.MapEngine()

    ## Test WGS84 pass through (input value should be )
    m.set_projection("EPSG:4326")

    geo_x, geo_y = 23, -27
    proj_x, proj_y = m.geo2proj(geo_x, geo_y)
    assert proj_x == geo_x
    assert proj_y == geo_y

    geo_x, geo_y = -45.001323, -12.106783
    proj_x, proj_y = m.geo2proj(geo_x, geo_y)
    assert proj_x == geo_x
    assert proj_y == geo_y

    geo_x, geo_y = [-45.001323, 38.43, 80.1], [-12.106783, 33.33103, 78.34565]
    proj_x, proj_y = m.geo2proj(geo_x, geo_y)
    assert proj_x == geo_x
    assert proj_y == geo_y

    geo_x, geo_y = "test", "test" ## Anything should pass through
    proj_x, proj_y = m.geo2proj(geo_x, geo_y)
    assert proj_x == geo_x
    assert proj_y == geo_y

    ## Test different projection
    m.set_projection("EPSG:32023")

    ## Test integer input with EPSG:32023
    geo_x, geo_y = 23, -27
    proj_x, proj_y = m.geo2proj(geo_x, geo_y)
    assert proj_x == pytest.approx(53296437.286, rel=0.001)
    assert proj_y == pytest.approx(4190499.797,  rel=0.001)

    ## Test float input with EPSG:32023
    geo_x, geo_y = -45.001323, -12.106783
    proj_x, proj_y = m.geo2proj(geo_x, geo_y)
    assert proj_x == pytest.approx(20888141.530, rel=0.001)
    assert proj_y == pytest.approx(-16812218.556,  rel=0.001)

    ## Test list input with EPSG:32023
    geo_x, geo_y = [-45.001323, 38.43, 80.1], [-12.106783, 33.33103, 78.34565]
    expct_x = [20888141.530, 28989822.199, 11406428.010]
    expct_y = [-16812218.556, 19662642.984, 28228459.400]
    proj_x, proj_y = m.geo2proj(geo_x, geo_y)

    for e_x, e_y, p_x, p_y in zip(expct_x, expct_y, proj_x, proj_y):
        assert p_x == pytest.approx(e_x, rel=0.001)
        assert p_y == pytest.approx(e_y, rel=0.001)

    ## Test if list result outputs np array
    assert isinstance(proj_x, np.ndarray)
    assert isinstance(proj_y, np.ndarray)

def test_proj2geo():
    """ Tests basic function of the proj2geo method """
    ## Create new MapEngine object for test
    m = MapEngine.MapEngine()

    ## Test WGS84 pass through (input value should be )
    m.set_projection("EPSG:4326")

    geo_x, geo_y = 23, -27
    proj_x, proj_y = m.geo2proj(geo_x, geo_y)
    assert proj_x == geo_x
    assert proj_y == geo_y

    geo_x, geo_y = -45.001323, -12.106783
    proj_x, proj_y = m.geo2proj(geo_x, geo_y)
    assert proj_x == geo_x
    assert proj_y == geo_y

    geo_x, geo_y = [-45.001323, 38.43, 80.1], [-12.106783, 33.33103, 78.34565]
    proj_x, proj_y = m.geo2proj(geo_x, geo_y)
    assert proj_x == geo_x
    assert proj_y == geo_y

    geo_x, geo_y = "test", "test" ## Anything should pass through
    proj_x, proj_y = m.geo2proj(geo_x, geo_y)
    assert proj_x == geo_x
    assert proj_y == geo_y

    ## Test different projection
    m.set_projection("EPSG:32023")

    ## Test integer input with EPSG:32023
    proj_x, proj_y = 53296437, 4190499
    geo_x, geo_y = m.proj2geo(proj_x, proj_y)
    assert geo_x == pytest.approx(23, rel=0.001)
    assert geo_y == pytest.approx(-27,  rel=0.001)


    ## Test float input with EPSG:32023
    proj_x, proj_y = 20888141.530, -16812218.556
    geo_x, geo_y = m.proj2geo(proj_x, proj_y)
    assert geo_x == pytest.approx(-45.001323, rel=0.001)
    assert geo_y == pytest.approx(-12.106783,  rel=0.001)

    ## Test list input with EPSG:32023
    expct_x = [-45.001323, 38.43, 80.1]
    expct_y = [-12.106783, 33.33103, 78.34565]
    proj_x = [20888141.530, 28989822.199, 11406428.010]
    proj_y = [-16812218.556, 19662642.984, 28228459.400]

    geo_x, geo_y = m.proj2geo(proj_x, proj_y)

    for e_x, e_y, g_x, g_y in zip(expct_x, expct_y, geo_x, geo_y):
        assert g_x == pytest.approx(e_x, rel=0.001)
        assert g_y == pytest.approx(e_y, rel=0.001)

    ## Test if list result outputs np array
    assert isinstance(geo_x, np.ndarray)
    assert isinstance(geo_y, np.ndarray)

def test_proj2pix():
    """ Tests basic function of the proj2pix method """
    ## Create new MapEngine object for test
    m = MapEngine.MapEngine()

    ## Test with WGS86 projection and default scale
    m.set_projection("EPSG:4326")

    proj_x, proj_y = 23, -27
    pix_x, pix_y = m.proj2pix(proj_x, proj_y)
    assert pix_x == pytest.approx(301, rel=0.001)
    assert pix_y == pytest.approx(310,  rel=0.001)


    ## Test float input with EPSG:32023
    proj_x, proj_y = 40.65, -13.23
    pix_x, pix_y = m.proj2pix(proj_x, proj_y)
    assert pix_x == pytest.approx(340, rel=0.001)
    assert pix_y == pytest.approx(279,  rel=0.001)


    ## Test list input
    proj_x = [-45.001323, 38.43, 80.1]
    proj_y = [-12.106783, 33.33103, 78.34565]
    expct_x = [150, 335, 427]
    expct_y = [277, 176, 77]

    pix_x, pix_y = m.proj2pix(proj_x, proj_y)

    for e_x, e_y, a_x, a_y in zip(expct_x, expct_y, pix_x, pix_y):
        assert a_x == pytest.approx(e_x, rel=0.001)
        assert a_y == pytest.approx(e_y, rel=0.001)

    
    ## Test different projection, location, and scale
    m.set_projection("EPSG:32023")
    m.set_scale(300)
    m.set_location(40, -83)

    ## Test integer input with EPSG:32023
    proj_x, proj_y = 53296437, 4190499
    pix_x, pix_y = m.proj2pix(proj_x, proj_y)
    assert pix_x == pytest.approx(52510, rel=0.001)
    assert pix_y == pytest.approx(-3267,  rel=0.001)


    ## Test float input with EPSG:32023
    proj_x, proj_y = 20888141.530, -16812218.556
    pix_x, pix_y = m.proj2pix(proj_x, proj_y)
    assert pix_x == pytest.approx(19583, rel=0.001)
    assert pix_y == pytest.approx(18072,  rel=0.001)


    ## Test list input with EPSG:32023
    proj_x = [20888141.530, 28989822.199, 11406428.010]
    proj_y = [-16812218.556, 19662642.984, 28228459.400]
    expct_x = [19583, 27814, 9949]
    expct_y = [18072, -18987, -27690]

    pix_x, pix_y = m.proj2pix(proj_x, proj_y)

    for e_x, e_y, a_x, a_y in zip(expct_x, expct_y, pix_x, pix_y):
        assert a_x == pytest.approx(e_x, rel=0.001)
        assert a_y == pytest.approx(e_y, rel=0.001)

    ## Test if list result outputs np array
    assert isinstance(pix_x, np.ndarray)
    assert isinstance(pix_y, np.ndarray)

