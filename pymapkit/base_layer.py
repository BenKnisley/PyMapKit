"""
Author: Ben Knisley [benknisley@gmail.com]
Date: 19 January, 2020
"""



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

    def activate(self):
        ''' Method called by _activate. Holds functions to be preformed to activate layer''' 
        pass
    
    def _deactivate(self):
        ''' Method called by parent Map object when self is removed from it '''
        self.parent = None
        self.deactivate()

    def deactivate(self):
        ''' Method called by parent Map object when self is removed from it '''
        pass


    def __repr__(self):
        ''' What string should represent the layer '''
        pass
    

    def get_extent(self):
        ''' Method that returns bounding box of all stored data'''
        pass
    
    def focus(self):
        ''' Method to move map to focus on layer '''
        pass
    
    def set_opacity(self):
        ''' Method to set opacity of whole layer '''
    
    def draw(self, renderer, canvas):
        ''' Method '''
        pass
