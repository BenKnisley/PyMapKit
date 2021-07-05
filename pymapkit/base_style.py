"""
Project: PyMapKit
Title: BaseStyle
Function: Holds BaseStyle Class
Author: Ben Knisley [benknisley@gmail.com]
Date: 8, June 2021
"""

class BaseStyle:
    """
    The BaseStyle class holds properties and adds methods to a parent object.
    It lets a user build a style profile using: add_domain, add_mode, and 
    add_property methods. A domain is set of modes and properties that are 
    independent of each other, like outline and fill. A mode is a way to render
    a domain and a set of properties that goes with that. For example: in the 
    fill domain of a polygon, you could have several modes: like solid color 
    fill or image fill. Both of these are separate modes with different 
    properties. A property is a named value, e.g. fill_color = 'red'
    """

    def __init__(self, feature):
        ## Store ref to styled feature
        self.feature = feature
        ## Whatever the user names style. feature.style has to be style
        self.feature.style = self

        ## Create Dict to hold domain mode properties
        self.domains = {}
        ## Create dict to hold current display modes
        self.current_modes = {}

        ## Create dict to hold property values
        self.managed_properties = {}

        self.cached_renderer_fn = None

    def __getitem__(self, key):
        return self.managed_properties[key]

    def add_domain(self, new_domain_name):
        self.domains[new_domain_name] = {}
        self.current_modes[new_domain_name] = None
        
        if new_domain_name:
            self.managed_properties[new_domain_name + '_mode'] = None
        
        self.create_domain_mode_etters(new_domain_name)

    def add_mode(self, new_mode_name, domain=None):

        if domain == None:
            if None not in self.domains:
                self.add_domain(None)

        self.domains[domain][new_mode_name] = {}

    def add_property(self, new_prop_name, default_value, mode=None, domain=None):
        if domain:
            self.domains[domain][mode][domain + '_' + new_prop_name] = default_value
        else:
            if mode:
                self.domains[domain][mode][new_prop_name] = default_value
            else:
                ## Add top level property
                self.managed_properties[new_prop_name] = default_value
                self.create_property_etters(new_prop_name)



    def set_mode(self, new_mode, domain=None):
        ## Get list of current properties
        current_mode = self.current_modes[domain]
        if current_mode:
            current_properties = list(self.domains[domain][current_mode].keys())
        else:
            current_properties = []

        ## Get list properties needed for new_mode
        incoming_properties = list(self.domains[domain][new_mode].keys())

        ## new_properties
        new_properties = [p for p in incoming_properties if p not in current_properties]
        old_properties = [p for p in current_properties if p not in incoming_properties]

        ## Remove old properties etters and from self.properties dict
        for prop in old_properties:
            self.remove_property_etters(prop)
            del self.managed_properties[prop]

        ## Create new property and its etters
        for prop in new_properties:
            self.managed_properties[prop] = self.domains[domain][new_mode][prop]
            self.create_property_etters(prop)
        
        self.current_modes[domain] = new_mode
        
        if domain:
            mode_prop_name = domain + '_mode'
        else:
            mode_prop_name = 'display_mode'

        self.managed_properties[mode_prop_name] = new_mode



    def create_domain_mode_etters(self, domain_name=None):

        ## Add domain setter to feature
        def set_display_template(self, new_value):
            self.style.set_mode(new_value, domain_name)
            self.style.clear_cache()
        
        if domain_name:
            setter_name = 'set_' + domain_name + '_display'
            getter_name = 'get_' + domain_name + '_display'
        else:
            setter_name = 'set_display'
            getter_name = 'get_display'

        bound_setter = set_display_template.__get__(self.feature, type(self.feature))
        self.feature.__dict__[setter_name] = bound_setter

        ## Add domain getter to feature
        def get_display_template(self):
            return self.style.current_modes[domain_name]

        ## Link, and bind set_display as a named method of the parent feature
        bound_getter = get_display_template.__get__(self.feature, type(self.feature))
        self.feature.__dict__[getter_name] = bound_getter

        ## Bind a getter to self too
        def get_display_template(self):
            return self.current_modes[domain_name]

        ## Link, and bind set_display as a named method of the parent feature
        bound_getter = get_display_template.__get__(self, type(self))
        self.__dict__[getter_name] = bound_getter

    def create_property_etters(self, property_name):

        ## Define [g][s]et_display templates
        def set_property_template(self, new_value):
            self.style.managed_properties[property_name] = new_value
            self.style.clear_cache()

        ## Link, and bind set_display as a named method of the parent feature
        bound_setter = set_property_template.__get__(self.feature, type(self.feature))
        self.feature.__dict__['set_'+property_name] = bound_setter

        def get_property_template(self):
            return self.style.managed_properties[property_name]

        ## Link, and bind set_display as a named method of the parent feature
        bound_getter = get_property_template.__get__(self.feature, type(self.feature))
        self.feature.__dict__['get_'+property_name] = bound_getter


        def get_property_template(self):
            return self.managed_properties[property_name]

        ## Link, and bind set_display as a named method of the parent feature
        bound_getter = get_property_template.__get__(self, type(self))
        self.__dict__['get_'+property_name] = bound_getter

    def remove_property_etters(self, property_name):
        del self.feature.__dict__['get_' + property_name]
        del self.feature.__dict__['set_' + property_name]

    def clear_cache(self):
        """
        This Method
        """
        self.cached_renderer_fn = None