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

def test_create_domain_mode_etters_inner_set_display_template():
    """ 
    Test BaseStyle.create_domain_mode_etters' inner function 
    set_display_template.
    """
    ## Creates a MockFeature and a BaseStyle Object
    f = MockFeature()
    s = pmk.BaseStyle(f)

    ## Add Mock methods called by set_display_template inner fn
    s.set_mode = MagicMock()
    s.clear_cache = MagicMock()

    ## Set style properties
    domain_name = None
    mode_name = 'TestMode'

    ## Call parent method which binds target inner function as f.set_display
    s.create_domain_mode_etters(domain_name)

    ## Call target function bound as f.set_display
    f.set_display(mode_name)
    
    ## Make assertions
    s.set_mode.assert_called_once_with(mode_name, domain_name)
    s.clear_cache.assert_called_once()

    ## Reset mocks
    s.set_mode.reset_mock()
    s.clear_cache.reset_mock()

    ## Set style properties
    domain_name = 'TestDomain'
    mode_name = 'TestMode2'

    ## Call parent method binding target inner fn as f.set_TestDomain_display
    s.create_domain_mode_etters(domain_name)

    ## Call target function bound as f.set_TestDomain_display
    f.set_TestDomain_display(mode_name)
    
    ## Make assertions
    s.set_mode.assert_called_once_with(mode_name, domain_name)
    s.clear_cache.assert_called_once()

def test_create_domain_mode_etters_inner_get_display_template():
    """ 
    Test BaseStyle.create_domain_mode_etters' inner functions
    feature_get_display_template style_get_display_template.
    """
    ## Creates a MockFeature and a BaseStyle Object
    f = MockFeature()
    s = pmk.BaseStyle(f)

    ## Add Mock methods called by set_display_template inner fn
    #s.set_mode = MagicMock()
    #s.clear_cache = MagicMock()

    ## Set style properties and style tree
    domain_name = None
    mode_name = 'TestMode'
    s.add_mode(mode_name, domain_name)

    ## Call parent method which binds target inner functions as f.get_display
    ## and s.get_display
    s.create_domain_mode_etters(domain_name)

    ## Set mode for getter methods to get
    s.set_mode(mode_name, domain_name)
    s.clear_cache()

    ## Call target function bound as f.set_display
    assert f.get_display() == s.current_modes[domain_name]
    assert s.get_display() == s.current_modes[domain_name]

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
    
def test_set_mode():
    """ Test BaseStyle.set_mode Method """
    f = MockFeature()
    s = pmk.BaseStyle(f)

    domain_name = "domain"
    mode0_name = "first_mode"
    mode1_name = "second_mode"
    prop1_name = 'prop1'; prop1_val = '123'
    prop2_name = 'prop2'; prop2_val = 'abc'

    ## Setup style tree
    s.add_domain(domain_name) 
    s.add_mode(mode0_name, domain_name)
    s.add_mode(mode1_name, domain_name)
    s.add_property(prop1_name, prop1_val, mode1_name, domain_name)
    s.add_property(prop2_name, prop2_val, mode1_name, domain_name)

    ## Update property names with prepended domain name
    prop1_name = domain_name + '_' + prop1_name
    prop2_name = domain_name + '_' + prop2_name
    
    ## Run set mode method
    s.set_mode(mode1_name, domain_name)

    ## Assert that current mode is set correctly
    assert s.current_modes[domain_name] == mode1_name

    ## Assert mode1 properties are in managed property dict
    assert prop1_name in s.managed_properties
    assert prop2_name in s.managed_properties

    ## Set to different mode 
    s.set_mode(mode0_name, domain_name)

    ## Assert that current mode changed
    assert s.current_modes[domain_name] == mode0_name

    ## Assert that properties are removed from managed_properties
    assert prop1_name not in s.managed_properties
    assert prop2_name not in s.managed_properties

    ## Assert that domain mode is in managaged properties
    mode_prop_name = domain_name + '_mode'
    assert mode_prop_name in s.managed_properties

    ## Test if mode is added none domain
    s.add_mode('my_mode', domain=None)
    s.set_mode('my_mode', domain=None)
    mode_prop_name = 'display_mode'
    assert mode_prop_name in s.managed_properties

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
    """ Test BaseStyle.create_domain_mode_etters Method """
    ## Creates a MockFeature and a BaseStyle Object
    f = MockFeature()
    s = pmk.BaseStyle(f)

    ## Set up MagicMock for clear_cache method
    s.clear_cache = MagicMock()
    
    ## Setup style tree for no domain
    domain_name = None
    mode_name = 'mode'
    prop_name = 'color'
    prop_value1 = 'orange'
    prop_value2 = 'green'
    s.add_domain(domain_name)
    s.add_mode(mode_name, domain_name)
    s.add_property(prop_name, prop_value1, mode_name, domain_name)
    s.set_mode(mode_name, domain_name)

    ## Call target function
    f.set_color(prop_value2)
    
    ## Make assertions
    assert s.managed_properties[prop_name] == prop_value2
    s.clear_cache.assert_called_once()
    s.clear_cache.reset_mock()
    
    ## Setup style tree for bingo domain
    domain_name = 'bingo'
    mode_name = 'mode1'
    prop_name = 'myprop'
    prop_value1 = 'val1'
    prop_value2 = 'val2'
    s.add_domain(domain_name)
    s.add_mode(mode_name, domain_name)
    s.add_property(prop_name, prop_value1, mode_name, domain_name)
    s.set_mode(mode_name, domain_name)

    ## Call target function
    f.set_bingo_myprop(prop_value2)

    ## Make assertions
    assert s.managed_properties[domain_name + '_' + prop_name] == prop_value2
    s.clear_cache.assert_called_once()
    
    '''
    Test Getters  
    '''
    assert s.get_color() == s.managed_properties['color']
    assert f.get_color() == s.managed_properties['color']
    assert s.get_bingo_myprop() == s.managed_properties['bingo_myprop']
    assert f.get_bingo_myprop() == s.managed_properties['bingo_myprop']

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