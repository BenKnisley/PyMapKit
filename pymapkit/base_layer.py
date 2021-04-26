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
        self.alpha = 1
        self.status = False ## Signals what the layer is doing or need done ==>
        ## => Such as 'loading', 'downloading', 'projecting', 'rendering', 'done'
    

    def _activate(self, new_parent):
        ''' Method called by parent Map object when self is added to it '''

        ## Raise exception if layer is already activated
        if self.map != None:
            raise Exception("Layer is already activated and belongs to a map object.")
        
        ## Set self.map to new parent
        self.map = new_parent

        ## Run child's activate method
        self.activate()

    @abc.abstractmethod
    def activate(self):
        ''' Method called by _activate. Holds functions to be preformed to activate layer''' 
        pass
    
    def _deactivate(self):
        ''' Method called by parent Map object when self is removed from it '''
        
        ## Raise exception if layer is not activated
        if self.map == None:
            raise Exception("Layer is not activated and does not belongs to a map object.")
        
        ## Remove parent map object and call child's deactivate method
        self.map = None
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
    
    def focus(self):
        ''' Method to move map to focus on layer '''

        ## If layer is not activated, raise Exception
        if self.map == None:
            raise Exception("Layer is not activated.")
        
        ## Get layer extent
        min_x, min_y, max_x, max_y = self.get_extent()

        ## Calculate center and set new map coord 
        proj_x = (max_x + min_x) / 2
        proj_y = (max_y + min_y) / 2
        self.map.set_projection_coordinates(proj_x, proj_y)

        ## If layer has no area, do not proceed 
        if (max_x - min_x) == 0 or (max_y - min_y) == 0:
            return

        ## Calculate best scale for layer
        s_x = (max_x - min_x) / self.map.width
        s_y = (max_y - min_y) / self.map.height
        new_scale = max(s_x, s_y)

        ## Scale out a bit
        new_scale = new_scale * 1.25

        ## Set newscale
        self.map.set_scale(new_scale, True)

    @abc.abstractmethod
    def clear_cache(self):
        pass

    def set_opacity(self, new_opacity):
        """
        Set the opacity of the whole layer.
        
        Args:
            opacity (float): New opacity value 0 to 1.

        Returns:
            None
        """
        self.alpha = new_opacity
    
    @abc.abstractmethod
    def render(self, renderer, canvas):
        ''' Method '''
        pass
