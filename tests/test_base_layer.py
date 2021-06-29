#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date: 29 June, 2020
"""
import pytest
from unittest.mock import MagicMock
import pymapkit as pmk


class MockMap:
    def __init__(self):
        ## Create a mock draw function
        self.set_projection_coordinates = MagicMock()
        self.set_scale = MagicMock()


def test_baselayer_init():
    """ Test BaseLayer.__init__ """
    l = pmk.base_layer.BaseLayer()

    ## Test if correct type
    assert isinstance(l, pmk.base_layer.BaseLayer)

    ## Test that init method created the correct placeholders
    assert "name" in l.__dict__
    assert "map" in l.__dict__
    assert "status" in l.__dict__

def test_baselayer_activate():
    """
    Test BaseLayer._activate method
    """
    ## Create a BaseLayer object and mock an activate method
    l = pmk.base_layer.BaseLayer()
    l.activate = MagicMock()

    ## Create a mock Map object
    mock_map = object()

    ## Call method
    l._activate(mock_map)

    ## Test that method added map object correctly
    assert l.map == mock_map

    ## Test that method called child activate method
    l.activate.assert_called_once()

    ## Test that method raises exception, when already activated
    with pytest.raises(Exception):
        l._activate(mock_map)

def test_baselayer_deactivate():
    """
    Test BaseLayer._deactivate method
    """
    ## Setup and mock activate a BaseLayer object
    l = pmk.base_layer.BaseLayer()
    l.deactivate = MagicMock()
    mock_map = object()
    l.map = mock_map

    ## Call method
    l._deactivate()

    ## Test that method removed map reference
    assert l.map == None

    ## Test that method would called impelmented deactivate method
    l.deactivate.assert_called_once()

    ## Test that method raises exception when already deactivated
    with pytest.raises(Exception):
        l._deactivate()


def test_baselayer_focus():
    """
    Test BaseLayer.focus method
    """
    ## Create BaseLayer and activated it with a new MockMap object
    l = pmk.base_layer.BaseLayer()
    mock_map = MockMap()
    l.map = mock_map

    ## width, height, min_x, min_y, max_x, max_y, scale, proj_x, proj_y
    param_list = [ 
        (500, 500, -40.0, 10.0, -34.0, 12.0, 0.015, -37.0, 11.0),
        (500, 500, -40.0, 10.0, 40.0, 91.0, 0.2025, 0.0, 50.5),
        (500, 500, 1120203, 3045943, 4562456, 5044342, 8605.6325, 2841329.5, 4045142.5),
        (1920, 1080, 1120203, 3045943, 4562456, 5044342, 2312.9618055555557, 2841329.5, 4045142.5),
        (1920, 1080, -40.0, 10.0, 40.0, 91.0, 0.09375, 0.0, 50.5),
    ]


    for width, height, min_x, min_y, max_x, max_y, scale, proj_x, proj_y in param_list:

        ## Setup a MockMap object
        mock_map.width = width
        mock_map.height = height
        l.get_extent = lambda: (min_x, min_y, max_x, max_y)
        
        ## Call method
        l.focus()

        ## Test that method calculated expected coordinates values
        mock_map.set_projection_coordinates.assert_called_once_with(proj_x, proj_y)
        mock_map.set_scale.assert_called_once_with(scale, True)

        ## Reset mocks
        mock_map.set_scale.reset_mock()
        mock_map.set_projection_coordinates.reset_mock()
