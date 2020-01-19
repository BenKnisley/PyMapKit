#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date:
"""

import MapEngine
from osgeo import ogr

## Setup driver for shapefile
driver = ogr.GetDriverByName('ESRI Shapefile')

## Read shapefile with single feature
sourceFile = driver.Open("./data/highland.shp", 0) # 0 means read-only.
sourceLayer = sourceFile.GetLayer()

points = []
for feature in sourceLayer:
    geom = feature.GetGeometryRef()
    for x in geom:
        cnt = 0
        for p in x.GetPoints():
            cnt += 1
            if cnt == 5:
                cnt = 0
                points.append( (p[1], p[0]) )



map = MapEngine.MapEngine()


print(len(points))

x = map.geo2pix(points)

for p in x:

    print(p)
