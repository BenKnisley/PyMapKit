"""
Author: Ben Knisley [benknisley@gmail.com]
Date: 19 January, 2020
"""
import abc

class BaseLayer:
    """
    A class defining a map layer. A base class for all other map layer classes
    to be derived. Contains common functionality and abstract method.
    """
    def __init__(self):
        """
        Initialize a BaseLayer object.
        Setup instance variables: map, name, and status.

        Args:
            None
    
        Returns:
            None
        """
        ## Required Attributes
        self.map = None ## Holds the parent map when activated
        self.name = None ## Holds the name of the layer
        self.status = False ## Signals what the layer is doing or need done ==>
        ## => Such as 'loading', 'downloading', 'projecting', 'rendering', 'done'
    
    def _activate(self, new_parent):
        '''
        Start activating the layer. 

        This method is called when the layer object is added to a Map object.
        It saves a reference to the map object as self.map, then calls the 
        subclassed layer's 'activate' method to complete activation.

        Args:
            new_parent (Map): The map object that has added and
    
        Returns:
            None
        '''
        ## Raise exception if layer is already activated
        if self.map != None:
            raise Exception("Layer is already activated and belongs to a map object.")
        
        ## Set self.map to new parent
        self.map = new_parent

        ## Run child's activate method
        self.activate()

    def _deactivate(self):
        '''
        Start deactivating the layer. 

        This method is called when the layer object is removed from a Map 
        object. It removes the reference to the map object, then calls the 
        subclassed layer's 'deactivate' method to complete deactivation.

        Args:
            None
    
        Returns:
            None
        '''
        ## Raise exception if layer is not activated
        if self.map == None:
            raise Exception("Layer is not activated and does not belongs to a map object.")
        
        ## Remove parent map object and call child's deactivate method
        self.map = None
        self.deactivate()

    def focus(self):
        ''' 
        Focus on the layer.

        Sets the parent map's scale and location to best showcase the layer.
        Requires that layer object is activated, and child layer class has 
        get_extent method properly implemented.

        Args:
            None
    
        Returns:
            None
        '''
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
    def __repr__(self):
        '''
        Abstract method to be implemented by child layer. 
        Magic method for generating a string representation of the layer.

        Args:
            None
    
        Returns:
            repr_str (str): A string representation of the layer.
        '''
        return "BaseLayer Object"
    
    @abc.abstractmethod
    def activate(self):
        '''
        Abstract method to be implemented by child layer. 
        Contains any code required by a layer to fully activate it with the new
        map object. Called by BaseLayer._activate after it adds the parent map 
        object to the layer.

        Args:
            None
    
        Returns:
            None
        '''
        pass
    
    @abc.abstractmethod
    def deactivate(self):
        ''' 
        Abstract method to be implemented by child layer. 
        Contains any code required by a layer to fully deactivate and reset it.
        Called by BaseLayer._deactivate which actually removes the map object 
        from the layer.

        Args:
            None
    
        Returns:
            None
        '''
        pass

    @abc.abstractmethod
    def get_extent(self):
        ''' 
        Abstract method to be implemented by child layer. 
        Returns the extent of the data in projection coordinates.
        
        Args:
        None
    
        Returns:
            min_x (float): The minimum x projection coordinate of the data.
            min_y (float): The minimum y projection coordinate of the data.
            max_x (float): The maximum x projection coordinate of the data.
            max_y (float): The maximum y projection coordinate of the data.
        '''
        pass

    @abc.abstractmethod
    def render(self, renderer, canvas):
        ''' 
        Abstract method to be implemented by child layer. 
        Draws the layer onto a canvas using the renderer.

        Args:
        renderer (BaseRenderer): The renderer to use to draw on the canvas.

        canvas (Unknown): The canvas to draw on.
    
        Returns:
            None
        '''
        pass
