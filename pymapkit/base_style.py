"""
Project: PyMapKit
Title: BaseStyle
Function: Holds BaseStyle Class
Author: Ben Knisley [benknisley@gmail.com]
Date: 8, June 2021
"""



class BaseStyle:
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
        self.managed_properties[new_domain_name + '_mode'] = None
        self.create_domain_mode_etters(new_domain_name)

    def add_mode(self, domain, new_mode_name):
        self.domains[domain][new_mode_name] = {}

    def add_property(self, new_prop_name, default_value):
        self.managed_properties[new_prop_name] = default_value
        self.create_property_etters(new_prop_name)

    def add_mode_property(self, domain, mode, new_prop_name, default_value):
        self.domains[domain][mode][domain + '_' + new_prop_name] = default_value

    def set_mode(self, domain, new_mode):
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
        self.managed_properties[domain + '_mode'] = new_mode


    def create_domain_mode_etters(self, domain_name):

        ## Add domain setter to feature
        def set_display_template(self, new_value):
            self.style.set_mode(domain_name, new_value)
            self.style.clear_cache()
        
        bound_setter = set_display_template.__get__(self.feature, type(self.feature))
        self.feature.__dict__['set_' + domain_name + '_display'] = bound_setter

        ## Add domain getter to feature
        def get_display_template(self):
            return self.style.current_modes[domain_name]

        ## Link, and bind set_display as a named method of the parent feature
        bound_getter = get_display_template.__get__(self.feature, type(self.feature))
        self.feature.__dict__['get_'+ domain_name +'_display'] = bound_getter

        ## Bind a getter to self too
        def get_display_template(self):
            return self.current_modes[domain_name]

        ## Link, and bind set_display as a named method of the parent feature
        bound_getter = get_display_template.__get__(self, type(self))
        self.__dict__['get_'+ domain_name +'_display'] = bound_getter

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
        self.cached_renderer_fn = None