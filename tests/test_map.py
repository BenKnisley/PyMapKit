"""
Author: Ben Knisley [benknisley@gmail.com]
Date: 10 January, 2020
"""
import pytest
from unittest.mock import MagicMock
import pymapkit as pmk
import pyproj


class mock_layer:
    def __init__(self):
        ## Create a mock draw function
        self._activate = MagicMock()
        self._deactivate = MagicMock()
        self.draw = MagicMock()


def test_map_init():
    """ Test Map.__init__ """
    m = pmk.Map()
    assert isinstance(m, pmk.Map)


def test_map_add():
    """ Test Map.add adds layer to layer list"""
    m = pmk.Map()
    new_layer0 = mock_layer()
    new_layer1 = mock_layer()
    new_layer2 = mock_layer()
    new_layer3 = mock_layer()
    m.add(new_layer1)
    m.add(new_layer2)
    m.add(new_layer3)
    m.add(new_layer0, 0)

    assert len(m.layers) == 4, "Map.add method did not add layer to map object"
    assert m.layers[0] == new_layer0, "Map.add(index=0) method did not add layer to begining of list"
    assert m.layers[1] == new_layer1, "Map.add method did not add layer to end of list"
    assert m.layers[2] == new_layer2, "Map.add method did not add layer to end of list"
    assert m.layers[3] == new_layer3, "Map.add method did not add layer to end of list"
    new_layer1._activate.assert_called_once_with(m)


def test_map_remove():
    """ Test Map.add adds layer to layer list"""
    m = pmk.Map()
    new_layer1 = mock_layer()
    new_layer2 = mock_layer()
    new_layer3 = mock_layer()

    m.add(new_layer1)
    m.add(new_layer2)
    m.add(new_layer3)

    m.remove(new_layer3)

    assert len(m.layers) == 2, "Map.add method did not remove layer from map object"
    assert new_layer3 not in m.layers, "Map.add method did not remove correct layer from map object"
    new_layer3._deactivate.assert_called_once()


def test_set_projection():
    """ Test Map.set_projection method """
    m = pmk.Map()

    ## Hold these to test if changed
    old_transform_geo2proj = m.transform_geo2proj
    old_transform_proj2geo = m.transform_proj2geo

    ## Test set with text
    m.set_projection('EPSG:32023')

    ## Check that projected_crs is correct, geo_crs is the same, and that the transforms updated
    assert m.projected_crs == pyproj.crs.CRS("EPSG:32023")
    assert m.geographic_crs == pyproj.crs.CRS("EPSG:4326")
    assert m.transform_geo2proj.is_exact_same(old_transform_geo2proj) == False
    assert m.transform_proj2geo.is_exact_same(old_transform_proj2geo) == False


def test_set_geographic_crs():
    """ Test Map.set_projection method """
    m = pmk.Map()

    ##
    ## Test set with text
    ##

    ## Hold these to test if changed
    old_transform_geo2proj = m.transform_geo2proj
    old_transform_proj2geo = m.transform_proj2geo

    ## Call set_geographic_crs
    m.set_geographic_crs('EPSG:4267')

    ## Check that geographic_crs is correct, proj_crs is the same, and that the transforms updated
    assert m.geographic_crs == pyproj.crs.CRS("EPSG:4267")
    assert m.projected_crs == pyproj.crs.CRS("EPSG:3785")
    assert m.transform_geo2proj.is_exact_same(old_transform_geo2proj) == False
    assert m.transform_proj2geo.is_exact_same(old_transform_proj2geo) == False


def test_set_location():
    """ Test Map.set_projection method """
    m = pmk.Map()

    geographic_crs = pyproj.crs.CRS("EPSG:4326")
    projected_crs = pyproj.crs.CRS("EPSG:3785")
    m.set_geographic_crs(geographic_crs)
    m.set_projection(projected_crs)

    tranform = pyproj.Transformer.from_crs(geographic_crs, projected_crs)

    ## Basic case
    try_x, try_y = tranform.transform(40, -83)
    m.set_location(40, -83)
    assert m.proj_x == try_x
    assert m.proj_y == try_y

    ## Edge case - values to big
    try_x, try_y = tranform.transform(200, 200)
    m.set_location(200, 200)
    assert m.proj_x == try_x
    assert m.proj_y == try_y


def test_get_location():
    """ Test Map.get_projection method """
    m = pmk.Map()

    m.set_location(40.0, 83.0)
    lat, lon = m.get_location()
    assert lat == pytest.approx(40.0)
    assert lon == pytest.approx(83.0)

    m.set_location(-35, -83.0)
    lat, lon = m.get_location()
    assert lat == pytest.approx(-35)
    assert lon == pytest.approx(-83.0)

    m.set_location(35, -83.0)
    lat, lon = m.get_location()
    assert lat == pytest.approx(35)
    assert lon == pytest.approx(-83.0)

    m.set_location(-35.0, 83.1)
    lat, lon = m.get_location()
    assert lat == pytest.approx(-35.0)
    assert lon == pytest.approx(83.1)


def test_set_projection_coordinates():
    """ Test Map.set_projection_coordinates method """
    m = pmk.Map()
    m.set_projection("EPSG:3785")
    
    ## Set first test values
    test_x, test_y = 7453953, 5593228
    
    ## Call set_projection_coordinates method
    m.set_projection_coordinates(test_x, test_y)

    ## Test that the projection values changed
    assert m.proj_x == test_x
    assert m.proj_y == test_y


def test_get_projection_coordinates():
    """ Test Map.get_projection_coordinates method """
    m = pmk.Map()
    m.set_projection("EPSG:3785")
    
    ## Set first test values
    test_x, test_y = 7453953, 5593228
    
    ## Call set_projection_coordinates method
    m.set_projection_coordinates(test_x, test_y)

    ## Get Results from get_projection_coordinates 
    result_x, result_y = m.get_projection_coordinates()

    assert result_x == test_x
    assert result_y == test_y


def test_set_scale():
    """ Test Map.set_scale method """
    m = pmk.Map()

    ## Do basic it changed test
    old_proj_scale = m._proj_scale
    m.set_scale(50)
    assert m._proj_scale != old_proj_scale

    ## Test with US-Ft projection
    m.set_projection('EPSG:32023')
    m.set_scale(50)
    assert m._proj_scale == pytest.approx(164.042)


    ## Test with degree projection
    m.set_projection('EPSG:4326')
    m.set_scale(50)
    assert m._proj_scale == pytest.approx(0.000452202)


def test_get_scale():
    """ Test Map.get_scale method """
    m = pmk.Map()

    m.set_scale(50000)
    scale = m.get_scale()
    assert scale != pytest.approx(50000)

    ## Test after projection change
    m.set_projection('EPSG:4326')
    scale = m.get_scale()
    assert scale != pytest.approx(50000)


def test_set_size():
    """ Test Map.set_size method """
    m = pmk.Map()

    m.set_size(100, 100)
    assert m.width == 100
    assert m.height == 100

    m.set_size(500, 100)
    assert m.width == 500
    assert m.height == 100

    m.set_size(800, 1000)
    assert m.width == 800
    assert m.height == 1000




def test_geo2proj():
    pass