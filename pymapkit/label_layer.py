"""
Author: Ben Knisley [benknisley@gmail.com]
Date: 2 September, 2021
"""
from .base_layer import BaseLayer

class LabelLayer(BaseLayer):
    def __init__(self):
        """
        """
        ##
        BaseLayer.__init__(self)
        
        #self.tile_cache = TileCache(self) #! <---------------

        ## Create Name property
        self.name = "Label Layer"
        
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
