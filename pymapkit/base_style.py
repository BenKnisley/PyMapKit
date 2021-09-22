"""
Project: PyMapKit
Title: Dynamic Feature Styler
Function: Separates ...
Author: Ben Knisley [benknisley@gmail.com]
Date: 8 September, 2021
"""


class Style:
    """
    This class stores style properties and manages getter and setter methods for
    a given "Styled Feature". It allows for a user to build a style profile, and
    it will automatically manages properties and bind getter and setter methods 
    to the companion styled object. 
    """
    def __init__(self, styled_feature) -> None:
        """ Inits a new style object """
        self.feature = styled_feature
        self.my_properties = []
        self.managed_properties = {}
        self.domains = {}
        self.children_styles = []
        self.cached_renderer_fn = None

    def __getitem__(self, prop_name) -> object:
        """ Returns the value of a property anywhere in the style tree """
        return self.managed_properties[prop_name].value

    def add_property(self, prop_name, prop_value):
        """ Adds a top-level property to the style. """
        new_prop = StyleProperty(self, prop_name, prop_value)
        self.managed_properties[prop_name] = new_prop
        self.my_properties.append(new_prop)
        new_prop.bind_etters()

    def add_domain(self, domain_name):
        """ Adds a domain to the style """
        new_domain = StyleDomain(self, domain_name)
        self.domains[domain_name] = new_domain
        new_domain.bind_mode_setter()
        return new_domain

    def add_child_style(self, child_style):
        self.children_styles.append(child_style)




class StyleDomain:
    def __init__(self, parent_style, domain_name) -> None:
        ## Store domain name & references to parent style, and styled feature
        self.name = domain_name
        self.style = parent_style
        self.feature = parent_style.feature
        
        ## Store a list of properties managed by self domain
        self.my_properties = []

        ## Store a dict of avabile modes, and the current active mode
        self.my_modes = {}
        self.active_mode = None
        
        ## Add a property in the parent style for the current active mode
        domain_mode_property_name = self.name + '_mode'
        new_prop = StyleProperty(parent_style, domain_mode_property_name, None)
        self.style.managed_properties[domain_mode_property_name] = new_prop

    def add_property(self, prop_name, prop_value):
        ''' Adds a property to the domain '''
        ## Prepend domain name to property name, & generate a property instance
        updated_prop_name = self.name + '_' + prop_name
        new_prop = StyleProperty(self.style, updated_prop_name, prop_value)
        
        ## Add new property instance to selfs & parent styles' property lists
        self.style.managed_properties[updated_prop_name] = new_prop
        self.my_properties.append(new_prop)
        
        ## Bind property getter and setter to styled feature
        new_prop.bind_etters()

    def add_mode(self, mode_name):
        """
        """
        new_mode = StyleMode(self, mode_name)
        self.my_modes[mode_name] = new_mode
        return new_mode

    def set_mode(self, mode_name):
        """ ... """
        ## Deactivate old mode
        if self.active_mode:
            self.active_mode.deactivate()
        
        if mode_name == None:
            self.active_mode = None
        else:
            ## Activate new mode
            new_mode = self.my_modes[mode_name]
            new_mode.activate()

            ##
            domain_mode_property_name = self.name + '_mode'
            self.style.managed_properties[domain_mode_property_name].value = mode_name

        ## Clear rendering function cache
        self.style.cached_renderer_fn = None

        for child_style in self.style.children_styles:
            child_style.domains[self.name].set_mode(mode_name)

    def bind_mode_setter(self):
        """
        ...
        """

        ### <START INNER FUNCTION LOGIC>
        ## ...
        domain_name = self.name
        style_self = self.style

        def set_mode_template(self, new_mode_name):
            ## Set mode for features' style
            style_self.domains[domain_name].set_mode(new_mode_name)
            
            ## Set mode for all children styles as well
            for child_style in style_self.children_styles:
                child_style.domains[domain_name].set_mode(new_mode_name)

        ### <END INNER FUNCTION LOGIC>
        
        ## Setup a doc string for the method
        set_mode_template.__doc__ = f"Sets ...///... {self.name}"

        ## Create a name for the setter method
        setter_name = 'set_' + self.name + '_mode'
        
        ## Link, and bind set_display as a named method of the parent feature
        bound_setter = set_mode_template.__get__(self.feature, type(self.feature))

        ## Add inner function as an entry in feature.__dict__
        self.feature.__dict__[setter_name] = bound_setter


class StyleMode:
    def __init__(self, parent_domain, mode_name) -> None:
        self.domain = parent_domain
        self.style = self.domain.style
        self.feature = self.domain.feature

        ## Store modes name
        self.name = mode_name

        self.my_properties = [] ## Switch to dict
    
    def add_property(self, prop_name, prop_value):
        updated_prop_name = self.domain.name + '_' + prop_name
        new_prop = StyleProperty(self.style, updated_prop_name, prop_value)
        self.my_properties.append(new_prop)
    
    def activate(self):
        for prop in self.my_properties:
            self.style.managed_properties[prop.name] = prop
            prop.bind_etters()

    def deactivate(self):
        """ """
        for prop in self.my_properties:
            del self.style.managed_properties[prop.name]
            prop.unbind_etters()


class StyleProperty:
    def __init__(self, parent_style, name, init_value) -> None:
        """ """
        ## Store the name and value of the property
        self.name = name
        self.value = init_value

        ## Store a reference to the parent style object and the parent feature
        self.style = parent_style
        self.feature = parent_style.feature
    
    def get_value(self):
        """ """
        return self.value
    
    def set_value(self, new_value):
        """ """
        ## Change to new value
        self.value = new_value
        self.style.cached_renderer_fn = None

        ## Call set_value on all children_styles
        for child_style in self.style.children_styles:
            child_style.managed_properties[self.name].set_value(new_value)

    def bind_etters(self):
        """ """

        ### <START INNER FUNCTION LOGIC>
        
        prop = self ## Rereference self as prop, because self will be different 
        # in bound methods

        def set_prop_template(self, new_value):
            prop.set_value(new_value)
        
        def get_prop_template(self):
            return prop.get_value()

        ### <END INNER FUNCTION LOGIC> """
        
        ## Setup a doc string for the method
        set_prop_template.__doc__ = f"Sets {self.name}"
        get_prop_template.__doc__ = f"Gets {self.name}"

        ## Create names for getter and setter methods
        setter_name = 'set_' + self.name
        getter_name = 'get_' + self.name
        
        ## Link, and bind set_display as a named method of the parent feature
        bound_setter = set_prop_template.__get__(self.feature, type(self.feature))
        bound_getter = get_prop_template.__get__(self.feature, type(self.feature))

        ## Add inner function as an entry in feature.__dict__
        self.feature.__dict__[setter_name] = bound_setter
        self.feature.__dict__[getter_name] = bound_getter
    
    def unbind_etters(self):
        """ """
        setter_name = 'set_' + self.name
        getter_name = 'get_' + self.name
        del self.feature.__dict__[setter_name]
        del self.feature.__dict__[getter_name]
