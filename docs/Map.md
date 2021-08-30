Class pymapkit.Map
==

The pymapkit.Map class creates Map objects, a object representing a map. It stores map attributes, holds map layers, and directs rendering.

## Methods
---

### classmethod ```__init__(...)```
Parameters:
None

Returns: A new pymapkit.Map object


### classmethod ```add(new_layer, index=-1)```
Adds a new layer to the map.
By default the new layer is added to the end of the layer list, and thus on top of existing map layers.

__Parameters:__
- new_layer - a pymapkit.MapLayer object to be added to the Map objects layer list

__Optional Parameters:__
- index(default=-1): the index where to insert the new layer. -1 adds layer to the top of the map, 0 to the bottom.

__Returns:__ None


### classmethod ```remove(del_layer)```
Removes a layer from the map.

__Parameters:__
- del_layer - the layer to remove from the layer list. del_layer must exist in map.layers.

__Optional Parameters:__
- None

__Returns:__ 
- None