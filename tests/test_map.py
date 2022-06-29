"""
Author: Ben Knisley [benknisley@gmail.com]
Date: 10 January, 2020
"""
import pytest
import unittest.mock as mock
from unittest.mock import MagicMock
from pytest_mock import mocker
import pymapkit as pmk
import pyproj
import numpy as np

'''
class MockLayer:
    def __init__(self):
        ## Create a mock draw function
        self.activate = MagicMock()
        self._activate = MagicMock()
        self._deactivate = MagicMock()
        self.render = MagicMock()
'''

class MockLayer(pmk.base_layer.BaseLayer):
    def __new__(cls, *args, **kwargs):
        return mock.Mock(spec=cls)

class mock_renderer:
    def __init__(self):
        ## Create a mock draw function
        self.is_canvas = MagicMock()
        self.is_canvas.return_value = True
        self.save = MagicMock()
        self.draw_background = MagicMock()


def test_map_init():
    """ Test Map.__init__ """
    m = pmk.Map()
    assert isinstance(m, pmk.Map)

    ## Test 'renderer' Optional Arg string input
    m = pmk.Map(renderer='pyskia')
    assert isinstance(m.renderer, pmk.SkiaRenderer)

    ## Test 'renderer' Optional Arg object input
    r = pmk.SkiaRenderer()
    m = pmk.Map(renderer=r)
    assert r == m.renderer

def test_add():
    """ 
    Test that Map.add correctly adds a layers to the layer list in the correct 
    order.
    """
    ## Create Map object for testing
    m = pmk.Map()

    ## Create mock layers
    new_layer1 = MockLayer()
    new_layer2 = MockLayer()
    new_layer3 = MockLayer()

    ## Test that add method adds a the layer to the Map.layers list
    m.add(new_layer1)
    assert len(m.layers) == 1
    assert m.layers[0] == new_layer1
    ## Test that BaseLayer._activate was called
    new_layer1._activate.assert_called_once_with(m)

    ## Test that method adds layers in correct order
    m.add(new_layer2)
    assert len(m.layers) == 2
    assert m.layers[1] == new_layer2
    ## Test that BaseLayer._activate was called
    new_layer2._activate.assert_called_once_with(m)

    ## Test that method adds layers at correct index
    m.add(new_layer3, 1)
    assert len(m.layers) == 3
    assert m.layers[1] == new_layer3
    ## Test that BaseLayer._activate was called
    new_layer2._activate.assert_called_once_with(m)

def test_add_type_constraints():
    """ Tests that Map.add raises TypeError with given bad inputs. """
    ## Create Map object for testing
    m = pmk.Map()

    ## Create test data
    new_layer = MockLayer()
    bad_type_input = 'This is a string'

    ## Test raising TypeError when a bad type is given as new_layer
    with pytest.raises(TypeError):
        m.add(bad_type_input)
    
    ## Test raising TypeError when a bad type is given as index
    with pytest.raises(TypeError):
        m.add(new_layer, bad_type_input)

def test_remove():
    """ 
    Tests that Map.remove removes layer from layer list, and calls 
    BaseLayer._activate method.
    """
    ## Create Map object for testing
    m = pmk.Map()

    ## Create mock layers
    test_layer1 = MockLayer()
    test_layer2 = MockLayer()
    test_layer3 = MockLayer()

    ## Add layer to map, without add method
    m.layers.append(test_layer1)
    m.layers.append(test_layer2)
    m.layers.append(test_layer3)

    ## Call remove method
    m.remove(test_layer2)

    ## Test that layer was removed
    assert test_layer2 not in m.layers
    assert len(m.layers) == 2

    ## Test that _deactivate method was called
    test_layer2._deactivate.assert_called_once()

def test_remove_type_constraints():
    """ Tests that Map.remove type constrain """
    ## Create Map object for testing
    m = pmk.Map()

    ## Create mock layers
    not_layer = 'not layer'

    ## Add not_layer to layer list, should never happen
    m.layers.append(not_layer)

    with pytest.raises(TypeError):
        m.remove(not_layer)

    ## Confirm was not removed
    assert not_layer in m.layers

def test_remove_exist_constraints():
    """ Tests that Map.remove does not call  """
    ## Create Map object for testing
    m = pmk.Map()

    ## Create mock layers
    test_layer = MockLayer()

    ## Check ValueError is raised when remove is called on layer not in m.layers
    with pytest.raises(ValueError):
        m.remove(test_layer)
    
    ## Confirm was layer was not added, & _deactivate was not called
    assert test_layer not in m.layers
    test_layer._deactivate.assert_not_called()

def test_set_projection():
    """ Test Map.set_projection method """
    m = pmk.Map()

    ## Add mock layers to map, and reset mocked activate method
    mock_layer1 = MockLayer()
    mock_layer2 = MockLayer()
    m.add(mock_layer1)
    m.add(mock_layer2)
    mock_layer1.activate.reset_mock()
    mock_layer2.activate.reset_mock()

    ## Hold these to test if changed
    old_transform_geo2proj = m.transform_geo2proj
    old_transform_proj2geo = m.transform_proj2geo

    ## Test unsupported input type raises exception
    with pytest.raises(Exception):
        m.set_projection(3)

    ## Test set with text
    m.set_projection('EPSG:32023')

    ## Check that projected_crs is correct, geo_crs is the same, and that the transforms updated
    assert m.projected_crs == pyproj.crs.CRS("EPSG:32023")
    assert m.geographic_crs == pyproj.crs.CRS("EPSG:4326")
    assert m.transform_geo2proj.is_exact_same(old_transform_geo2proj) == False
    assert m.transform_proj2geo.is_exact_same(old_transform_proj2geo) == False

    ## Check that method calls layer activate method
    mock_layer1.activate.assert_called_once()
    mock_layer2.activate.assert_called_once()

def test_set_geographic_crs():
    """ Test Map.set_projection method """
    m = pmk.Map()

    mock_layer1 = MockLayer()
    mock_layer2 = MockLayer()

    ## Add mock layers to map, and reset mocked activate method
    m.add(mock_layer1)
    m.add(mock_layer2)
    mock_layer1.activate.reset_mock()
    mock_layer2.activate.reset_mock()

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

    ## Check that method calls layer activate method
    mock_layer1.activate.assert_called_once()
    mock_layer2.activate.assert_called_once()

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

    ## Test with US-Ft projection with proj_units True
    m.set_scale(50, True)
    assert m._proj_scale == pytest.approx(50)


    ## Test with degree projection
    m.set_projection('EPSG:4326')
    m.set_scale(50)
    assert m._proj_scale == pytest.approx(0.000452202)

def test_get_scale():
    """ Test Map.get_scale method """
    m = pmk.Map()

    m.set_scale(50000)
    scale = m.get_scale()
    assert scale == pytest.approx(50000)

    ## Test after projection change, that should change scale
    m.set_projection('EPSG:4326')
    scale = m.get_scale()
    assert scale == pytest.approx(50000)

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

def test_get_size():
    """ Test Map.get_size method """
    m = pmk.Map()

    m.set_size(100, 100)
    assert m.get_size()[0] == 100
    assert m.get_size()[1] == 100


    m.width = 350
    assert m.get_size()[0] == 350
    assert m.get_size()[1] == 100

    m.height = 410
    assert m.get_size()[0] == 350
    assert m.get_size()[1] == 410

def test_zoom_in():
    """ Test Map.zoom_in method """
    m = pmk.Map()

    ## Default scale change
    m._proj_scale = 5000
    m.zoom_in()
    assert m._proj_scale == 3333.3333333333335


    ## Factor arg scale change
    m._proj_scale = 5000
    m.zoom_in(2)
    assert m._proj_scale == 2500

def test_zoom_out():
    """ Test Map.zoom_out method """
    m = pmk.Map()

    ## Default scale change
    m._proj_scale = 5000
    m.zoom_out()
    assert m._proj_scale == 7500


    ## Factor arg scale change
    m._proj_scale = 5000
    m.zoom_out(2)
    assert m._proj_scale == 10000

def test_set_renderer(mocker):
    """ Test Map.get_renderer method """
    m = pmk.Map()

    ## Test directly setting renderer object
    fake_renderer_obj = object()
    m.set_renderer(fake_renderer_obj)
    assert m.renderer == fake_renderer_obj

    ## Test that setting renderer from string calls get_renderer correctly
    fake_renderer_obj = object()
    get_renderer_patch = mocker.patch("pymapkit.map.get_renderer", return_value=fake_renderer_obj)
    m.set_renderer("fake_renderer")
    get_renderer_patch.assert_called_once_with("fake_renderer")
    assert m.renderer == fake_renderer_obj

def test_get_renderer():
    """ Test map.get_renderer function """
    ## Test pyskia
    return_obj = pmk.map.get_renderer('pyskia')
    assert isinstance(return_obj, pmk.skia_renderer.SkiaRenderer)

def test_render():
    """ Test map.render method """
    m = pmk.Map()

    mock_renderer_obj = mock_renderer()
    m.set_renderer(mock_renderer_obj)

    ## Create mock layers
    new_layer1 = MockLayer()
    new_layer2 = MockLayer()
    new_layer3 = MockLayer()

    ## Add layers to canvas
    m.add(new_layer1)
    m.add(new_layer2)
    m.add(new_layer3)

    ## Call render with no args
    m.render()

    ## Assert that draw_background was called
    mock_renderer_obj.draw_background.assert_called_once()

    ## Assert the each layer had draw method called
    new_layer1.render.assert_called_once_with(mock_renderer_obj, mock_renderer_obj)
    new_layer2.render.assert_called_once_with(mock_renderer_obj, mock_renderer_obj)
    new_layer3.render.assert_called_once_with(mock_renderer_obj, mock_renderer_obj)
    ## Assert that save was called 
    mock_renderer_obj.save.assert_called_once_with(mock_renderer_obj, None)

    ## Reset mock renderer
    mock_renderer_obj = mock_renderer()
    m.set_renderer(mock_renderer_obj)

    ## Call with file arg
    m.render("./file.png")

    ## Assert that save was called 
    mock_renderer_obj.save.assert_called_once_with(mock_renderer_obj, "./file.png")

def test_geo2proj():
    """ Test Map.geo2proj method """
    m = pmk.Map()
    m.set_geographic_crs('EPSG:4267') ## NAD84
    m.set_projection("EPSG:32023") ## Ohio South FT

    ## Test singlet integer input
    test_coord = (-83, 40)
    expected = (1859916.4298, 728826.5006)
    actual = m.geo2proj(*test_coord)
    assert expected[0] == pytest.approx(actual[0])
    assert expected[1] == pytest.approx(actual[1])

    ## Test list 
    test_coords = (
        [22.52, -3.13, -83.1, -77.1, np.inf], 
        [33.45, 43.80, -31.8, -22.9, np.inf]
        # value
    )

    ## NOTE: (inf,inf) ==> (inf,inf) => (5169978.7942,-26917578.0576)>
    #> AKA the last good value
    expected = (
        [27416968.3248, 20414646.4987, 1606378.3434, 5169978.7942,  np.inf], 
        [15047776.1068, 10772468.3457, -33210736.0296, -26917578.0576, np.inf]
    )

    actual = m.geo2proj(*test_coords)

    ## Assert output is list
    assert isinstance(actual[0], list)
    assert isinstance(actual[1], list)

    ## Test for expected results
    for actual_x, actual_y, expected_x, expected_y in zip(*actual, *expected):
        assert expected_x == pytest.approx(actual_x)
        assert expected_y == pytest.approx(actual_y)

def test_proj2geo():
    """ Test Map.proj2geo method """
    m = pmk.Map()
    m.set_geographic_crs('EPSG:4267') ## NAD84
    m.set_projection("EPSG:32023") ## Ohio South FT

    ## Test singlet integer input
    test_coord = (1859916, 728826)
    expected = (-83, 40)
    actual = m.proj2geo(*test_coord)
    assert expected[0] == pytest.approx(actual[0])
    assert expected[1] == pytest.approx(actual[1])


    ## Test list 
    test_coords = (
        [27416968.3248, 20414646.4987, 1606378.3434, 5169978.7942, np.inf], 
        [15047776.1068, 10772468.3457, -33210736.0296, -26917578.0576, np.inf]
    )
    
    expected = (
        [22.52, -3.13, -83.1, -77.1, np.inf], 
        [33.45, 43.80, -31.8, -22.9, np.inf]
    )

    actual = m.proj2geo(*test_coords)

    ## Assert output is list
    assert isinstance(actual[0], list)
    assert isinstance(actual[1], list)

    ## Test for expected results
    for actual_x, actual_y, expected_x, expected_y in zip(*actual, *expected):
        assert expected_x == pytest.approx(actual_x)
        assert expected_y == pytest.approx(actual_y)

def test_proj2pix():
    """ Test Map.proj2pix method """
    ## Setup parameters
    m = pmk.Map()
    m.set_geographic_crs('EPSG:4267') ## NAD84
    m.set_projection("EPSG:32023") ## Ohio South FT
    m.set_size(500, 500)
    m.set_location(40, -83)
    m.set_scale(5000)

    ## Test singlet input
    test_coord = (m.proj_x, m.proj_y)
    expected = (250, 250) ## Half of canvas size
    actual = m.proj2pix(*test_coord)
    assert expected[0] == pytest.approx(actual[0])
    assert expected[1] == pytest.approx(actual[1])

    ## Test list input
    test_coords = (
        [27416968.3248, 20414646.4987, 1606378.3434, 5169978.7942], 
        [15047776.1068, 10772468.3457, -33210736.0296, -26917578.0576]
    )

    expected = (
        [1808, 1381, 235, 452], 
        [-623, -362, 2319, 1935]
    )

    actual = m.proj2pix(*test_coords)

    ## Assert output is list
    assert isinstance(actual[0], list)
    assert isinstance(actual[1], list)

    ## Test for expected results
    for actual_x, actual_y, expected_x, expected_y in zip(*actual, *expected):
        assert expected_x == pytest.approx(actual_x, 0.1)
        assert expected_y == pytest.approx(actual_y, 0.1)

def test_pix2proj():
    """ Test Map.pix2proj method """
    ## Setup parameters
    m = pmk.Map()
    m.set_geographic_crs('EPSG:4267') ## NAD84
    m.set_projection("EPSG:32023") ## Ohio South FT
    m.set_size(500, 500)
    m.set_location(40, -83)
    m.set_scale(5000)

    ## Test singlet input
    test_coord = (250, 250) ## Half of canvas size
    expected = (m.proj_x, m.proj_y) 
    actual = m.pix2proj(*test_coord)
    assert expected[0] == pytest.approx(actual[0])
    assert expected[1] == pytest.approx(actual[1])

    
    ## Test list input
    test_coords = (
        [1808, 1381, 235, 452], 
        [1123, 862, -1819, -1435]
    )

    expected = (
        [27416968.3248, 20414646.4987, 1606378.3434, 5169978.7942], 
        [15047776.1068, 10772468.3457, -33210736.0296, -26917578.0576]
    )
    
    actual = m.pix2proj(*test_coords)

    ## Assert output is list
    assert isinstance(actual[0], list)
    assert isinstance(actual[1], list)

    ## Test for expected results
    for actual_x, actual_y, expected_x, expected_y in zip(*actual, *expected):
        assert expected_x == pytest.approx(actual_x, abs=5000*2)
        assert expected_y == pytest.approx(actual_y, abs=5000*2)
    
def test_geo2pix():
    """ Test Map.geo2pix method """
    ## Setup parameters
    m = pmk.Map()
    m.set_geographic_crs('EPSG:4267') ## NAD84
    m.set_projection("EPSG:32023") ## Ohio South FT
    m.set_size(500, 500)
    m.set_location(40, -83)
    m.set_scale(5000)

    ## Test singlet input
    test_coord = (-83, 40)
    expected = (250, 250) 
    actual = m.geo2pix(*test_coord)
    assert expected[0] == pytest.approx(actual[0])
    assert expected[1] == pytest.approx(actual[1])
    
    ## Test list input
    test_coords = (
        [22.52, -3.13, -83.1, -77.1], 
        [33.45, 43.80, -31.8, -22.9]
    )

    expected = (
        [1808, 1381, 235, 452], 
        [-623, -362, 2319, 1935]
    )
    
    actual = m.geo2pix(*test_coords)

    ## Assert output is list
    assert isinstance(actual[0], list)
    assert isinstance(actual[1], list)

    ## Test for expected results
    for actual_x, actual_y, expected_x, expected_y in zip(*actual, *expected):
        assert expected_x == pytest.approx(actual_x, 0.1)
        assert expected_y == pytest.approx(actual_y, 0.1)
    
def test_pix2geo():
    """ Test Map.pix2geo method """
    ## Setup parameters
    m = pmk.Map()
    m.set_geographic_crs('EPSG:4267') ## NAD84
    m.set_projection("EPSG:32023") ## Ohio South FT
    m.set_size(500, 500)
    m.set_location(40, -83)
    m.set_scale(5000)

    ## Test singlet input
    test_coord = (250, 250) 
    expected = (-83, 40)
    actual = m.pix2geo(*test_coord)
    assert expected[0] == pytest.approx(actual[0])
    assert expected[1] == pytest.approx(actual[1])
    
    ## Test list input
    test_coords = (
        [1808, 1381, 235, 452], 
        [1123, 862, -1819, -1435]
    )

    expected = (
        [22.52, -3.13, -83.1, -77.1], 
        [33.45, 43.80, -31.8, -22.9]
    )
    
    actual = m.pix2geo(*test_coords)

    ## Assert output is list
    assert isinstance(actual[0], list)
    assert isinstance(actual[1], list)

    ## Test for expected results
    for actual_x, actual_y, expected_x, expected_y in zip(*actual, *expected):
        assert expected_x == pytest.approx(actual_x , abs=0.1)
        assert expected_y == pytest.approx(actual_y , abs=0.1)