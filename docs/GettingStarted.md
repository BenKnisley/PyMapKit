PyMapKit QuickStart Guide
==

Welcome to the PyMapKit QuickStart Guide. This guide will give a quick 
introduction to using PyMapKit for making maps. 

There are two requirements before we proceed.
Make sure you have PyMapKit installed, and that you have some data to visualize.
If you need some data to get started: download a sample dataset.


## A Minimal Application
The simplest PyMapKit script looks like this.

```Python
import pymapkit as pmk

m = pmk.Map()

counties = pmk.VectorLayer.from_path("./data/ohio_counties.geojson")

m.add(counties)

counties.focus()

m.render('./MyMap.png')
```

So what happened there? 

1. We imported the pymapkit library, using "pmk" for brevity.

2. We created a Map object.

3. Then we created a layer, in this case we created a VectorLayer.

4. Next we call the focus method on that layer. This moves the map to showcase
that layer.

5. Finally, we call the render method on the Map object. This creates an image
file of our map.