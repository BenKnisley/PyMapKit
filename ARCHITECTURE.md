PyMapKit Project Architecture
==
This document outlines the basic design architecture for PyMapKit.

---
## Basic Classes
There are three main classes to know about before working on PyMapKit:
- Renderer Classes
- Layer Classes
- Map Class

The basic functions of these classes are:

* A **Map** manages map properties, stores map layers, and controls the rendering pipeline

* A **Renderer** contains functionality for drawing on a specific backend, while exposing a consistent drawing API

* A **Layer** utilizes the drawing API to render a specific type of data


The basic relationship between these classes is:

* A Map object stores a single renderer object

* A Map object can store many map layers in an ordered list

* The Map.render method will call layer.render for each stored layer. The layer will use the map renderer object to draw itself onto the canvas.

---
---

## Map Class
The Map class is the central class of the PyMapKit project. 
It has three primary functions: 

- Handle map properties

- Hold and manage map layers

- Manage the rendering pipeline

You can derive a new class from the Map class to fit specific applications, such as building a map widget.

---
## Layer Classes
A map layer class implements loading and rendering a certain type of data. 
Here are two are two built-in layers as an example:

* The VectorLayer class implements loading and rendering geographic vector data

* The StaticText class implements rendering unanchored text

A new layer class should be created for each new type of data you want to display.
You can easily created a new layer class by deriving from and implementing all required methods of the BaseLayer abstract class. 

A couple important layer attributes & methods to know about are:

**Layer.map** is a attribute referencing the parent map object.

**Layer.activate** is the method called when the layer is added to a new map instance.

**Layer.render** is the method called by the parent map object to draw the layer.


---
## Renderer Classes
A renderer class provides a consistent drawing API for a specific backend.
The drawing API is defined by the BaseRenderer class, and every derived class must implement each drawing method with the specific backend. 

A great example of a renderer is the default renderer: SkiaRenderer. 
The SkiaRenderer class is derived from the BaseRenderer, and implements each required method using PySkia.

The drawing API can be extended by adding deriving a new renderer class and adding custom drawing methods.