"""
Author: Ben Knisley [benknisley@gmail.com]
Date: 19 January, 2020
"""
import abc

class BaseLayer:
    def __init__(self):
        ## Required Attributes
        self.name = None ## Holds the name of the layer
        self.map = None ## Holds the parent map when activated
        self.status = False ## Signals what the layer is doing or need done ==>
        ## => Such as 'loading', 'downloading', 'projecting', 'rendering', 'done'
    

    def _activate(self, new_parent):
        ''' Method called by parent Map object when self is added to it '''
        self.map = new_parent
        self.activate()

    @abc.abstractmethod
    def activate(self):
        ''' Method called by _activate. Holds functions to be preformed to activate layer''' 
        pass
    
    def _deactivate(self):
        ''' Method called by parent Map object when self is removed from it '''
        self.parent = None
        self.deactivate()

    @abc.abstractmethod
    def deactivate(self):
        ''' Method called by parent Map object when self is removed from it '''
        pass

    @abc.abstractmethod
    def __repr__(self):
        ''' What string should represent the layer '''
        pass
    
    @abc.abstractmethod
    def get_extent(self):
        ''' Method that returns bounding box of all stored data'''
        pass
    
    @abc.abstractmethod
    def focus(self):
        ''' Method to move map to focus on layer '''
        pass
    
    @abc.abstractmethod
    def set_opacity(self):
        ''' Method to set opacity of whole layer '''
    
    @abc.abstractmethod
    def render(self, renderer, canvas):
        ''' Method '''
        pass
