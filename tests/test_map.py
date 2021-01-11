"""
Author: Ben Knisley [benknisley@gmail.com]
Date: 10 January, 2020
"""
import pytest
from unittest.mock import MagicMock
import pymapkit as pmk


class mock_layer:
    def __init__(self):
        ## Create a mock draw function
        self.activate = MagicMock()
        self.deactivate = MagicMock()
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
    new_layer1.activate.assert_called_once_with(m)


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
    new_layer3.deactivate.assert_called_once()
