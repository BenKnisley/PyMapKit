#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date:
"""
from __future__ import absolute_import

import pytest
import MapEngine


def test_MapEngine_initiation():
    """ Test initiation of MapEngine Object  """
    MapEngine.MapEngine()


def test_MapEngine_set_size_1():
    """ Test initiation of MapEngine Object  """
    m = MapEngine.MapEngine()
    m.set_size(1000, 1000)


def test_MapEngine_set_size_neg_input():
    """ Test initiation of MapEngine Object  """
    m = MapEngine.MapEngine()
    with pytest.raises(Exception):
        ## Should fail
        m.set_size(-1000, -1000)


def test_MapEngine_set_size_float_input():
    """ Test initiation of MapEngine Object  """
    m = MapEngine.MapEngine()
    with pytest.raises(Exception):
        ## Should fail
        m.set_size(100.8, 100.2)

"""
def good_fail_example():
    map_obj = MapEngine.MapEngine()
    with pytest.raises(Exception):
        assert map_obj.bingo
"""