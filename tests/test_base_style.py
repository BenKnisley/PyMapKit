#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date: 29 June, 2020
"""
import pytest
from unittest.mock import Base, MagicMock
import pymapkit as pmk


class MockMap:
    def __init__(self):
        ## Create a mock draw function
        self.set_projection_coordinates = MagicMock()
        self.set_scale = MagicMock()


class MockFeature:
    def __init__(self):
        self.style = None


def test_base_style_init():
    """ Test BaseStyle.__init__ Method """
    f = MockFeature()
    s = pmk.BaseStyle(f)
    assert isinstance(s, pmk.BaseStyle)

def test_create_domain_mode_etters():
    """ Test BaseStyle.create_domain_mode_etters Method """
    ## Creates a MockFeature and a BaseStyle Object
    f = MockFeature()
    s = pmk.BaseStyle(f)

    ## Call method without args
    s.create_domain_mode_etters()
    
    ## Assert that method binds methods correctly
    ## Does not test bound methods
    assert "set_display" in f.__dict__
    assert "get_display" in f.__dict__
    assert "get_display" in s.__dict__
    
    ## Call method with domain set domain_name
    s.create_domain_mode_etters(domain_name='test')
    
    ## Assert that method binds methods correctly
    ## Does not test bound methods
    assert "set_test_display" in f.__dict__
    assert "get_test_display" in f.__dict__
    assert "get_test_display" in s.__dict__

def test_create_domain_mode_etters_inner_fns():
    assert True


def test_add_domain():
    """ Test BaseStyle.add_domain Method """
    f = MockFeature()
    s = pmk.BaseStyle(f)
    
    ## Call method
    domain_name = 'bingo'
    s.add_domain(domain_name)

    ## Assert that domain key was added to domain dict
    assert domain_name in s.domains

    ## Assert that the new domain's value is an empty dict
    assert s.domains[domain_name] == {}
    
    ## Assert that a managed property key was added for new domain
    assert s.managed_properties[domain_name + '_mode'] == None

    ## Assert that the method calls create_domain_mode_etters for new domain
    assert "set_" + domain_name + "_display" in f.__dict__
    assert "get_" + domain_name + "_display" in f.__dict__


    ## Call method again
    domain_name = 'test2'
    s.add_domain(domain_name)

    ## Assert that domain key was added to domain dict
    assert domain_name in s.domains

    ## Assert that the new domain's value is an empty dict
    assert s.domains[domain_name] == {}
    
    ## Assert that a managed property key was added for new domain
    assert s.managed_properties[domain_name + '_mode'] == None

    ## Assert that the method calls create_domain_mode_etters for new domain
    assert "set_" + domain_name + "_display" in f.__dict__
    assert "get_" + domain_name + "_display" in f.__dict__

def test_add_mode():
    """ Test BaseStyle.add_mode Method """
    f = MockFeature()
    s = pmk.BaseStyle(f)

    mode_name = "mode_1"
    s.add_mode(mode_name)

    ## Assert that None domain was added to domain dict when adding domainless
    # mode
    assert None in s.domains

    ## Assert that mode was added to the the None domain
    assert s.domains[None] == {mode_name:{}}

    ## With Domain test
    domain_name = "domain1"
    mode_name = "mode_2"

    s.add_domain(domain_name)
    s.add_mode(mode_name, domain_name)

    ## Assert that mode was added to the the correct domain
    assert s.domains[domain_name] == {mode_name:{}}


def test_add_property():
    """ Test BaseStyle.add_property Method """
    f = MockFeature()
    s = pmk.BaseStyle(f)
    
    ## Test adding property top-level
    prop_name = 'flavor'
    prop_val = 'apple_cin'
    s.add_property(prop_name, prop_val)
    assert s.managed_properties[prop_name] == prop_val

    ## Test with mode
    mode_name = "mode_1"
    prop_name = 'my_prop'
    prop_val = 'abc123'
    s.add_mode(mode_name)
    s.add_property(prop_name, prop_val, mode_name)
    assert s.domains[None][mode_name][prop_name] == prop_val

    ## Test with mode
    domain_name = "bingo"
    mode_name = "mode_2"
    prop_name = 'my_prop2'
    prop_val = 'bingo_val'
    s.add_domain(domain_name)
    s.add_mode(mode_name, domain_name)
    s.add_property(prop_name, prop_val, mode_name, domain_name)
    assert s.domains[domain_name][mode_name][domain_name + '_' + prop_name] == prop_val
    

def test_create_property_etters():
    """ Test BaseStyle.create_property_etters Method """
    ## Creates a MockFeature and a BaseStyle Object
    f = MockFeature()
    s = pmk.BaseStyle(f)

    s.create_property_etters('bingo')

    assert "set_bingo" in f.__dict__
    assert "get_bingo" in f.__dict__
    assert "get_bingo" in s.__dict__

def test_create_property_etters_inner_fns():
    pass

def test_clear_cache():
    """ Test BaseStyle.clear_cache Method """
    ## Create a parent object, and a BaseStyle object
    f = MockFeature()
    s = pmk.BaseStyle(f)

    ## Set a cached renderer
    s.cached_renderer_fn = object()

    ## Call method
    s.clear_cache()

    ## Test that the renderer was cleared
    assert s.cached_renderer_fn == None


    