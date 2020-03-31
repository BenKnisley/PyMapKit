#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date:
"""
from __future__ import absolute_import

import math
import pytest
import pyproj
import MapEngine

def test_initiation():
    """ Test initiation of MapEngine Object  """
    m = MapEngine.MapEngine()
    assert isinstance(m, MapEngine.MapEngine)

def test_defaults():
    m = MapEngine.MapEngine()
    assert m._WGS84 == pyproj.Proj("EPSG:4326"), "_WGS84 projection not EPSG:4326"
    assert isinstance(m._layer_list, list), "_layer_list not type list"
    assert len(m._layer_list) == 0, "_layer_list already has content"
    assert m._projection == pyproj.Proj("EPSG:4326"), "Default projection not EPSG:4326" 
    assert m._scale == 1.0
    assert m.height == 500
    assert m.width == 500
    assert m.longitude == 0.0
    assert m.latitude == 0.0
    assert m._background_color == (0.05, 0.05, 0.05)

def test_init_args():
    m = MapEngine.MapEngine( projection="EPSG:3735", scale=500, longitude=-82.1, latitude=40.0, width=600, height=500)
    assert m._WGS84 == pyproj.Proj("EPSG:4326")
    assert m._projection == pyproj.Proj("EPSG:3735")
    assert m._scale == 500
    assert m.width == 600
    assert m.height == 500
    assert math.isclose(m.longitude, -82.1, rel_tol=1e-9, abs_tol=0.0)
    assert math.isclose(m.latitude, 40.0, rel_tol=1e-9, abs_tol=0.0)

def test_get_size():
    """ Test initiation of MapEngine Object  """
    m = MapEngine.MapEngine()
    
    m.set_size(800, 500)
    assert m.get_size() == (800, 500)
    assert m.width == 800
    assert m.height == 500

    m.set_size(1000, 2000)
    assert m.get_size() == (1000, 2000)
    assert m.width == 1000
    assert m.height == 2000

def test_set_size():
    """ Test initiation of MapEngine Object  """
    m = MapEngine.MapEngine()
    m.set_size(600, 500)
    assert m.get_size() == (600, 500)

    m.width = 50
    m.height = 45

    assert m.get_size() == (50, 45)
    assert m.width == 50
    assert m.height == 45

def test_set_size_bad_input():
    """  """
    m = MapEngine.MapEngine()

    with pytest.raises(Exception):
        m.set_size("Hello", "World")
    
    with pytest.raises(Exception):
        m.set_size([1,4,5], [70,56,5])

    with pytest.raises(Exception):
        m.set_size(-400, -300)
    
    with pytest.raises(Exception):
        m.set_size(500, -530)
    
    with pytest.raises(Exception):
        m.set_size(-500, 530)

    with pytest.raises(Exception):
        m.set_size(100.8, 100)
    
    with pytest.raises(Exception):
        m.set_size(100, 100.2)
    
    with pytest.raises(Exception):
        m.set_size(0, 0)
    
    with pytest.raises(Exception):
        m.set_size(0, 100)

    with pytest.raises(Exception):
        m.set_size(100, 0)

    with pytest.raises(Exception):
        m.width = -100
    
    with pytest.raises(Exception):
        m.height = -100

    with pytest.raises(Exception):
        m.width = 400.3
    
    with pytest.raises(Exception):
        m.height = 300.1

def test_get_scale():
    """ """
    m = MapEngine.MapEngine()
    
    m.set_scale(100.043)
    assert m.get_scale() == 100.043

    m.set_scale(0.000032)
    assert m.get_scale() == 0.000032

def test_set_scale():
    """ """
    m = MapEngine.MapEngine()
    
    m.set_scale(100.043)
    assert m.get_scale() == 100.043

    m.set_scale(0.000032)
    assert m.get_scale() == 0.000032

def test_set_scale_bad_input():
    """ """
    m = MapEngine.MapEngine()
    
    with pytest.raises(Exception):
        m.set_scale("Hello World")
    
    with pytest.raises(Exception):
        m.set_scale(0)
    
    with pytest.raises(Exception):
        m.set_scale(-1)
    
    with pytest.raises(Exception):
        m.set_scale(-10000)

def test_get_location():
    """ """
    ##
    m = MapEngine.MapEngine()
    m.set_location(-82.0, 40.0)
    
    ##
    coord = m.get_location() 
    assert math.isclose(coord[0], -82.0, rel_tol=1e-9, abs_tol=0.0)
    assert math.isclose(coord[1], 40.0, rel_tol=1e-9, abs_tol=0.0)

    ##
    assert math.isclose(m.latitude, 40.0, rel_tol=1e-9, abs_tol=0.0)
    assert math.isclose(m.longitude, -82.0, rel_tol=1e-9, abs_tol=0.0)
    
def test_set_location():
    """ """
    m = MapEngine.MapEngine()
    m.set_location(-82.0, 40.0)
    
    coord = m.get_location() 
    assert math.isclose(coord[0], -82.0, rel_tol=1e-9, abs_tol=0.0)
    assert math.isclose(coord[1], 40.0, rel_tol=1e-9, abs_tol=0.0)

    m.set_location(0.0, 0.0)
    coord = m.get_location() 
    assert math.isclose(coord[0], 0.0, rel_tol=1e-9, abs_tol=0.0)
    assert math.isclose(coord[1], 0.0, rel_tol=1e-9, abs_tol=0.0)

    m.latitude = 47.678
    m.longitude = -32.1
    coord = m.get_location() 
    assert math.isclose(coord[0], -32.1, rel_tol=1e-9, abs_tol=0.0)
    assert math.isclose(coord[1], 47.678, rel_tol=1e-9, abs_tol=0.0)

    m.latitude = -10.0
    coord = m.get_location() 
    assert math.isclose(coord[0], -32.1, rel_tol=1e-9, abs_tol=0.0)
    assert math.isclose(coord[1], -10.0, rel_tol=1e-9, abs_tol=0.0) 

    m.longitude = 67.1
    coord = m.get_location() 
    assert math.isclose(coord[0], 67.1, rel_tol=1e-9, abs_tol=0.0)
    assert math.isclose(coord[1], -10.0, rel_tol=1e-9, abs_tol=0.0) 

def xtest_set_location_bad_input():
    """ """
    m = MapEngine.MapEngine()

    with pytest.raises(Exception):
        m.set_location(0, 91) ## lat too large
    
    with pytest.raises(Exception):
        m.set_location(0, -91) ## lat too large
    
    with pytest.raises(Exception):
        m.set_location(181, 0) ## lon too large
    
    with pytest.raises(Exception):
        m.set_location(-181, 0) ## lon too large
    
    with pytest.raises(Exception):
        m.latitude = 91

    with pytest.raises(Exception):
        m.latitude = -91

    with pytest.raises(Exception):
        m.longitude = 181
    
    with pytest.raises(Exception):
        m.longitude = -181

    with pytest.raises(Exception):
        m.set_location('break', 'break')

    with pytest.raises(Exception):
        m.latitude = 'break'
    
    with pytest.raises(Exception):
        m.longitude = 'break'


"""
TODO: Write Tests for these functions
 - def get_projection
 - def set_projection
 - set_proj_coordinate
 - get_proj_coordinate
 - add_layer
 - remove_layer
 - get_layer
 - render
 - geo2proj
 - proj2geo
 - proj2pix
 - pix2proj
 - geo2pix
 - pix2geo
"""