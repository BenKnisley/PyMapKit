#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date: January 12, 2020
"""
## Import PyProj, and numpy
import pyproj
from pyproj import Transformer, transform
import numpy as np


def geo2proj(geo_data, WGS84_proj, dest_proj):
    """
    """

    ## If dest_proj is WGS84, no convert is needed, pass geo_data to output
    if WGS84_proj == dest_proj:
        return geo_data

    transformer = Transformer.from_proj(WGS84_proj, dest_proj)

    ## If geo_data is a list
    if isinstance(geo_data, list):

        lon = [coord[0] for coord in geo_data]
        lat = [coord[1] for coord in geo_data]

        lon = np.array(lon)
        lat = np.array(lat)

        #x, y = pyproj.transform(WGS84_proj, dest_proj, lat, lon)
        x, y = transformer.transform(lat, lon)

        proj_data = list( zip(x,y) )

    else:
        lon, lat = geo_data
        x, y = pyproj.transform(WGS84_proj, dest_proj, lat, lon) ## alwaysXy
        #x,y = y,x
        proj_data = (x, y)

    return proj_data


def proj2geo(proj_data, WGS84_proj, source_proj):
    """ """
    x, y = projPoint
    lon, lat = pyproj.transform(WGS84_proj, source_proj, x, y)
    geo_data = (lat, lon)
    return geo_data


def proj2pix():
    pass

def pix2proj():
    pass

def geo2pix():
    pass

def pix2geo():
    pass
