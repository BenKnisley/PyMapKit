#!/usr/bin/env python3
"""
Project: PyMapKit
Title: Simple Vector Data Example
Function: Demonstrate simple rendering a simple map with vector data 
Author: Ben Knisley [benknisley@gmail.com]
Created: 18 July, 2020
"""
## Import PyMapKit
import PyMapKit

## Create a PyMapKit Map object
m = PyMapKit.Map()

## Create a new vector data layer from a geojson file
ohio_counties = PyMapKit.VectorLayer("./examples/data/ohio_counties.geojson")

## Add layer to Map 
m.add_layer(ohio_counties)

## Focus on layer
ohio_counties.focus()

## Render map to file
m.render("./ohio_counties.png")
