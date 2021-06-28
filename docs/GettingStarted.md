PyMapKit QuickStart Guide
==

Welcome to the PyMapKit QuickStart Guide. This guide should give a quick 
introduction to using PyMapKit for making maps. 

There are two requirements before we proceed.
Make sure you have PyMapKit installed, and that you have some data to visualize.
If you need some data to get started: download a sample dataset.


```
Outline
1. A Minimal Application
2. Changing Map Parameters
3. Visualizing Vector Data
4. Visualizing Raster Data
5. Displaying Map Tiles
6. Changing Background display
```



## A Minimal Application
One of the simplest possible PyMapKit scripts looks like this. This creates a
map from a geojson file.

```python
import pymapkit as pmk

m = pmk.Map()

counties = pmk.VectorLayer.from_path("./data/ohio_counties.geojson")
m.add(counties)
counties.focus()

m.render('./MyMap.png')
```

So what happened there? Let us go through it line by line.




 ## Changing Map Parameters

### Changing Projection



## Visualizing Vector Data

To create a new 

```python
counties = pmk.VectorLayer.from_path("./data/ohio_counties.geojson")
```