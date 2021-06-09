"""
Project: PyMapKit
Title: BaseStyle
Function: Holds BaseStyle Class
Author: Ben Knisley [benknisley@gmail.com]
Date: 8, June 2021
"""
from operator import methodcaller


class BaseStyle:
    def __init__(self, styled_feature):
        '''
        '''
        ## Store reference to styled feature 
        self.feature = styled_feature

        ## Store list of display modes
        self.display_modes = {
        #> 'name', properties, defaults
        'none': ([], []) ## None is always an option 
        }
        
        ## Create current style placeholder
        self.display = 'none'

        ## Create list to hold current style properties for to feature 
        self.dynamic_properties = []
        
        ## Create list to hold current methods bound to feature 
        self.dynamic_methods = []

        ## Create and bind get and set display methods to styled feature
        self.create_display_etters()

        ## Create a placeholder for cached rendering function
        self.cached_renderer_fn = None
    
    def add_display_mode(self, mode_name, prop_list, default_vals):
        """
        Creates a new display mode
        
        Creates a new display mode, by adding details to display_modes dict. 
        To be used by a child class to create display modes for specific 
        targets.
        """
        self.display_modes[mode_name] = (prop_list, default_vals)

    def set_display(self, new_mode):
        ## Check if new_mode is valid, if yes then set display value
        if new_mode in self.display_modes:
            self.display = new_mode
        else:
            raise ValueError(f"'{new_mode}' not a valid display mode.")
        
        ## Get property names & default values from ChildClass.display_modes
        properties, defaults = self.display_modes[new_mode]
        
        ## Create a dict to hold defaults for properties
        defaults_dict = {p:d for p,d in zip(properties, defaults)}

        ## Get lists of exclusively new a& old dynamic properties
        old_props = [p for p in self.dynamic_properties if p not in properties]
        new_props = [p for p in properties if p not in self.dynamic_properties]

        ## Remove property from self & dynamic_properties if in old_props
        for prop in old_props:
            del self.__dict__[prop]
            del self.feature.__dict__['get_' + prop]
            del self.feature.__dict__['set_' + prop]
            self.dynamic_properties.remove(prop)

        ## For property exclusively in new_prop, add default val
        for prop in new_props:
            self.feature.style.__dict__[prop] = defaults_dict[prop]
            self.dynamic_properties.append(prop)

            ## Create getter and setter for each new property
            self.create_property_methods(prop)
    
    def create_display_etters(self):
        """
        Creates and binds get_display, and set_display to styled feature
        """
        ## Define set_display template
        def set_display_templ(self, new_value):
            ## call set display on style 
            self.style.set_display(new_value)
            self.style.cached_renderer_fn = None

        
        ## Define get_display template
        def get_display_templ(self):
            return self.style.__dict__['display']
        
        ## Link, and bind set_display as a named method of the parent feature
        bound_setter = set_display_templ.__get__(self.feature, type(self.feature))
        self.feature.__dict__['set_display'] = bound_setter

        ## Link, and bind set_display as a named method of the parent feature
        bound_getter = get_display_templ.__get__(self.feature, type(self.feature))
        self.feature.__dict__['get_display'] = bound_getter

    def create_property_methods(self, prop_name):

            ## Define a property setter method
            def setter_template(self, new_value):
                self.style.__dict__[prop_name] = new_value
                self.clear_cache()

            ## Define a property getter method
            def getter_template(self):
                return self.style.__dict__[prop_name]
            
            ## Bind setter and getter to parent feature
            bound_setter = setter_template.__get__(self.feature, type(self.feature))
            bound_getter = getter_template.__get__(self.feature, type(self.feature))

            ## Link bound_setter as a named method
            self.feature.__dict__['set_'+prop_name] = bound_setter
            self.feature.__dict__['get_'+prop_name] = bound_getter

            ## Add getter and setter names to dynamic_methods list
            self.dynamic_methods.append('set_'+prop_name)
            self.dynamic_methods.append('get_'+prop_name)
    
