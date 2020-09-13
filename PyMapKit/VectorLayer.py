"""
Project: PyMapKit
Title: VectorLayer
Function: Holds Classes for Rendering Vector Data
Author: Ben Knisley [benknisley@gmail.com]
Created: 20 July, 2020
"""
import os
import math
import warnings
import numpy as np
import ogr

class VectorFeature:
    """
    A base class representing a Vector feature

    Holds data structures and methods for attribute data & geometric data common 
    to all types of vector features. Each derived class must provide structures 
    and methods for drawing, and type specific features.
    """

    def __init__(self, parent):
        """
        Instantiates a new VectorFeature object

        Instantiates a new VectorFeature object inside of a derived class.

        Arguments:
            parent: The VectorLayer in which the VectorFeature object is added

        Returns:
            None
        """
        ## Set reference to parent VectorLayer object
        self.parent = parent

        ## Create a dictionary to hold attributes
        self.attribute_dict = {}

        ## Create a list to hold geometric structure of Vector feature
        self.geom_struct = []

        ## Store the start address in the common point sequence and the number of points
        self.init_address = len(self.parent.x_list)
        self.point_count = 0

    def __getitem__(self, key):
        """
        Returns the value of the given key
        """
        if isinstance(key, str):
            #key = self.parent.fields.index(key)
            return self.attribute_dict[key]
    
    def set_attributes(self, attributes):
        """
        Set the objects attributes to the given attributes

        Arguments:
            attributes: Ordered list of attribute values
    
        Returns:
            None
        """
        ## Loop through parent layers fields and given attributes
        for field_name, attribute in zip(self.parent.fields, attributes):
            ## Set attribute value
            self.attribute_dict[field_name] = attribute
    
    def fields(self):
        """
        Returns the names of the attribute fields

        Arguments:
        None

        Returns:
            fields: List of names of attribute fields
        """
        ## Return all keys in attribute dict
        return self.attribute_dict.keys()

    def from_gdal_feature(self, gdal_feature):
        """
        Imports attributes & geometry from a GDAL feature

        Arguments:
            gdal_feature: The gdal_feature to import data from

        Returns:
            None
        """
        ## Extract attributes from gdal feature
        for field in self.parent.fields:
            self.attribute_dict[field] = feature.GetField(field)

        ## Get gdal geom object from gdal feature
        geom = feature.GetGeometryRef()
        
        ## Extract geometry from gdal feature
        if geom.GetGeometryName() in ("POINT", "MULTIPOINT"):
            ## Plain point
            if geom.GetGeometryCount() == 0:
                x_list, y_list = [], []
                for point in geom.GetPoints():
                    x_list.append(point[0])
                    y_list.append(point[1])
                self.add_subgeometry(x_list, y_list)
            
            ## Mutipoint
            else:
                for indx in range(geom.GetGeometryCount()):
                    subpoly_geom = geom.GetGeometryRef(indx)

                    x_list, y_list = [], []
                    for point in subpoly_geom.GetPoints():
                        x_list.append(point[0])
                        y_list.append(point[1])
                    self.add_subgeometry(x_list, y_list)

        elif geom.GetGeometryName() in ("LINESTRING", "MULTILINESTRING"):
            geocount = geom.GetGeometryCount()
            if geocount == 0:
                x_list, y_list = [], []
                for point in geom.GetPoints():
                    x_list.append(point[0])
                    y_list.append(point[1])
                self.add_subgeometry(x_list, y_list)
            else:
                for indx in range(geom.GetGeometryCount()):
                    subgeom = geom.GetGeometryRef(indx)
                    
                    x_list, y_list = [], []
                    for point in subgeom.GetPoints():
                        x_list.append(point[0])
                        y_list.append(point[1])
                    self.add_subgeometry(x_list, y_list)

        elif geom.GetGeometryName() in ("POLYGON", "LINEARRING", "MULTIPOLYGON"):
            for indx in range(geom.GetGeometryCount()):
                subpoly_geom = geom.GetGeometryRef(indx)

                if subpoly_geom.GetGeometryName() == "POLYGON":
                    subpoly_geom = subpoly_geom.GetGeometryRef(0)

                x_list, y_list = [], []
                for point in subpoly_geom.GetPoints():
                    x_list.append(point[0])
                    y_list.append(point[1])
                self.add_subgeometry(x_list, y_list)

        else:
            print("There is an unexpected geometry type.")
            print(geom.GetGeometryName())
            print()

    def add_subgeometry(self, new_x_points, new_y_points):
        """
        Adds a new subgeometry to the feature

        Arguments:
            new_x_points: x points values of the new subgeometry
            new_y_points: y points values of the new subgeometry

        Returns:
            None
        """
        ## Add number of points in new subgeometry to features total point_count
        self.point_count += len(new_x_points)

        #self.geom_struct.append( (len(self.parent.x_list), len(new_x_points)) )
        
        ## Add point count to features geom_struct
        self.geom_struct.append(len(new_x_points))

        ## Add new points to common point sequences 
        self.parent.x_list += new_x_points
        self.parent.y_list += new_y_points

    def get_subgeometry(self, index):
        """
        Returns points belonging to subgeometry at given index

        Arguments:
            index: The index of the desired subgeometry

        Returns:
            x points: List of x values (projection coord), belonging to subgeometry.
            y points: List of y values (projection coord), belonging to subgeometry.
        """

        ## Find start address of subgeom in common point list
        init_point = self.init_address + sum(self.geom_struct[:index])
        
        ## Find last point belonging to subgeom in common point list
        geom_size = self.geom_struct[index]
        term_point = init_point + geom_size

        ## Get points from splices of common point sequences
        x_points = self.parent.x_list[init_point:term_point]
        y_points = self.parent.y_list[init_point:term_point]

        ## Return point lists
        return x_points, y_points
    
    def get_subgeometries(self):
        """
        Returns all subgeometries belonging to feature

        Arguments:
            index: The index of the desired subgeometry

        Returns:
            Returns a list of tuples of x and y values for each subgeometry
        """
        geom_list = []

        ## Add all subgeoms into geom_list
        for i in range(self.subgeometry_count()):
            geom_list.append(self.get_subgeometry(i))
        
        return geom_list

    def subgeometry_count(self):
        """
        Returns the number of subgeometries within the feature
        
        Arguments:
            None

        Returns:
            Subgeometry count: Number of subgeometries belonging to feature
        """
        return len(self.geom_struct)

    def get_points(self):
        """
        Returns all points belonging to feature

        Returns all points belonging to feature in two lists: x points & y points

        Arguments:
            None
    
        Returns:
            x points: List of x values (projection coord), belonging to feature.
            y points: List of y values (projection coord), belonging to feature.
        """
        ## Fetch points belong to feature from common point sequences
        x_points = self.parent.x_list[self.init_address:self.init_address+self.point_count]
        y_points = self.parent.y_list[self.init_address:self.init_address+self.point_count]
        
        ## Return point lists
        return x_points, y_points

    def get_extent(self):
        """
        Returns the extents (projection coordinates) of the feature

        Arguments:
            None

        Returns:
            min_x: The minimum x value of the feature
            min_y: The minimum y value of the feature
            max_x: The maximum x value of the feature
            max_y: The maximum y value of the feature
        """
        x_points, y_points = self.get_points()
        return min(x_points), min(y_points), max(x_points), max(y_points)

    def focus(self):
        """
        Sets the location and scale of the grandparent map object to showcase 
        the feature

        Requires:
            - Parent VectorLayer (parent) must be added to a Map object
        
        Arguments:
            - None 
        """
        min_x, min_y, max_x, max_y = self.get_extent()

        self.parent.parent._projx = (max_x + min_x)/2
        self.parent.parent._projy = (max_y + min_y)/2

        if (max_x - min_x) == 0 or (max_y - min_y) == 0:
            return

        s_x = (max_x - min_x) / self.parent.parent.width
        s_y = (max_y - min_y) / self.parent.parent.height

        new_scale =  max(s_x, s_y)

        ## Get projection crs dict, ignore all warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            crs_dict = self.parent.parent._projection.crs.to_dict()

        ## If units not defined in crs_dict the units are degrees
        if 'units' not in crs_dict:
            ## Convert scale to m/pix from deg
            new_scale = new_scale * 110570

        elif crs_dict['units'] == 'us-ft':
                new_scale = new_scale / 3.28084
        
        else:
            pass ## Is meters :) scale is already in m/pix
    
        new_scale = new_scale * 1.25

        ## Set processed newscale
        self.parent.parent.set_scale(new_scale)

class PointFeature(VectorFeature):
    """
    """

    def __init__(self, parent):
        """
        Instantiate a new Point Vector feature
        """
        ## Instantiate VectorFeature
        VectorFeature.__init__(self, parent)

        ## Set base style attributes (color, opacity, and radius)
        self._color = 'green' ## Default color is green
        self._opacity = 1
        self._radius = 2

        ## Init variable to cache color
        self._cached_color = None

    def set_color(self, input_color, opacity=1):
        """
        Sets the base color of the point
        """
        self._color = input_color
        self._opacity = opacity
        self._cached_color = None

    def set_weight(self, input):
        """
        Sets the size of the point
        """
        self._radius = input / 2.0

    def set_outline_color(self, input_color, opacity=1):
        """ """
        pass

    def set_outline_weight(self, input):
        """
        """
        pass
    
    def set_icon(self, input):
        """
        """
        pass

    def point_within(self, test_x, test_y):
        """
        Reports whether a given points is approximately collocated with point
        """
        for x_points, y_points in self.get_subgeometries():
            for point_x, point_y in zip(x_points, y_points):
                if(math.isclose(test_x, point_x, abs_tol=self.parent.parent._proj_scale*5) and
                    math.isclose(test_y, point_y, abs_tol=self.parent.parent._proj_scale*5)):
                    return True
        return False

    def draw(self, layer, renderer, cr, color_override=None):
        """
        Draws the point onto given canvas with given renderer
        """
        ## If color not cached yet, cache it
        if self._cached_color == None:
            self._cached_color = renderer.color_converter(self._color, opacity=(layer._alpha * self._opacity))
        
        if color_override:
            color = renderer.color_converter(color_override)
        else:
            color = self._cached_color

        ## Calculate pixel values
        pix_x, pix_y = layer.parent.proj2pix(*self.get_points())

        ## Draw point with renderer
        renderer.draw_point(cr, self.geom_struct, pix_x, pix_y, color, self._radius, layer._alpha)

class LineFeature(VectorFeature):
    """ """
    def __init__(self, parent):
        """ """
        VectorFeature.__init__(self, parent)
        self._color = 'red' ## Default color is green
        self._cached_color = None

        self._width = 1

    def set_color(self, input_color, opacity=1):
        """ """
        self._color = input_color
        self._line_opacity = opacity

        self._cached_color = None

    def set_weight(self, input_width):
        """ """
        self._width = input_width

    def set_outline_color(self, input_color):
        """ """
        pass

    def set_outline_weight(self, weight):
        """ """
        pass
    
    def set_style(self, input):
        """ """
        pass

    def point_within(self, test_x, test_y):
        ## Loop through each subgeom
        for x_points, y_points in self.get_subgeometries(): 
            ## Set first set of compair points to first point of subgeom
            x1, y1 = x_points[0], y_points[0]
            ## Compair each set of points to the last
            for x2, y2 in zip(x_points, y_points): 
                ## Only compair if points are different
                if (x1,y1) != (x2,y2):
                    ## Find distance between compare points (ab)
                    base = (( (x2-x1)**2 + (y2-y1)**2 )**0.5)

                    ## Find distances from test point to both compair points 
                    ac = (( (x1-test_x)**2 + (y1-test_y)**2 )**0.5)
                    bc = (( (x2-test_x)**2 + (y2-test_y)**2 )**0.5)

                    ## Only proceed if both ac & bc are smaller than base 
                    if (ac < base) and (bc < base):
                        ## Find area of triangle
                        area = ( x1*(y2-test_y) + x2*(test_y-y1) + test_x*(y1-y2) )/2

                        ## Find distance of test point from base line (height of triangle)
                        dist = (2*area) / base
                        ## Convert to pixel distance
                        pix_dist = dist / self.parent.parent._proj_scale

                        ## If distance is less than 10 pixels, then point is near enough
                        if pix_dist < 10:
                            return True
                ## Increment last point
                x1,y1 = x2,y2 
        return False

                    #if (area / squr_area) < 0.0001:
                    #   return True


        return False

    def draw(self, layer, renderer, cr, color_override=None):
        """ """
        ## If color not cached yet, cache it
        if self._cached_color == None:
            self._cached_color = renderer.color_converter(self._color, opacity=(layer._alpha * self._line_opacity))
        
        if color_override:
            color = renderer.color_converter(color_override)
        else:
            color = self._cached_color

        ## Calculate pixel values
        pix_x, pix_y = layer.parent.proj2pix(*self.get_points())
        renderer.draw_line(cr, self.geom_struct, pix_x, pix_y, self._width, color, layer._alpha)

class PolygonFeature(VectorFeature):
    """ """
    def __init__(self, parent):
        """ """
        ## Init base VectorFeature Class
        VectorFeature.__init__(self, parent)

        ## Create vars for background color
        self._bgcolor = "blue" #! Pick a better default
        self._bg_opacity = 1
        self._cached_bgcolor = None
        
        ## Create vars for line color
        self._line_color = "black"
        self._line_opacity = 1
        self._cached_line_color = None

        ## Property to hold line width
        self._line_width = 1

    def set_color(self, input_color, opacity=1):
        """ """
        ## Set color and opacity
        self._bgcolor = input_color
        self._bg_opacity = opacity

        ## Reset cached_bgcolor
        self._cached_bgcolor = None

    def set_outline_color(self, input_color, opacity=1):
        """ """
        self._line_color = input_color
        self._line_opacity = opacity
        self._cached_line_color = None

    def set_outline_weight(self, input_width):
        """ """
        self._line_width = input_width

    def point_within(self, test_x, test_y):
        ## Loop through each subgeom
        for x_points, y_points in self.get_subgeometries():
            inside = False
            n = len(x_points)
            p1x,p1y = x_points[0], y_points[0]
            for i in range(n+1):
                p2x, p2y = x_points[i % n], y_points[i % n]
                if test_y > min(p1y,p2y):
                    if test_y <= max(p1y,p2y):
                        if test_x <= max(p1x,p2x):
                            if p1y != p2y:
                                xints = (test_y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                            if p1x == p2x or test_x <= xints:
                                inside = not inside
                p1x,p1y = p2x,p2y
            if inside:
                return True
        return False

    def draw(self, layer, renderer, cr, color_override=None):
        """
        Draws the polygon

        Draws the polygon onto the canvas with the given renderer.

        ... 
        """
        if self._cached_line_color == None:
            self._cached_line_color = renderer.color_converter(self._line_color, opacity=(layer._alpha * self._line_opacity))

        if self._cached_bgcolor == None:
            self._cached_bgcolor = renderer.color_converter(self._bgcolor, opacity=(layer._alpha * self._bg_opacity))

        if color_override:
            bg_color = renderer.color_converter(color_override)
        else:
            bg_color = self._cached_bgcolor

        ## Calculate pixel values
        #""" ## Full layer vectorization proj2pix optimization
        #pix_x, pix_y = self._pix_x, self. _pix_y
        """ ## Single Vector iteration proj2pix
        pix_x, pix_y = layer.parent.proj2pix(self._proj_x, self._proj_y)
        #"""

        ## Calculate pixel values
        pix_x, pix_y = layer.parent.proj2pix(*self.get_points())
        
        ## Call on renderer to render polygon
        renderer.draw_polygon(cr, self.geom_struct, pix_x, pix_y, bg_color, self._line_width, self._cached_line_color, layer._alpha)

class VectorLayer:
    def __init__(self, path=None):
        self.parent = None
        self._alpha = 1

        self.name = "VectorLayer"

        ## Create list to hold features
        self.features = []
        
        ## Create List to hold fields
        self.fields = []

        ## Create lists to hold all points
        self.x_list = []
        self.y_list = []

        if path:
            ## Load Gdal from file extension
            driver_dict = {'.shp': 'ESRI Shapefile', '.geojson': 'GeoJSON'}
            try:
                driver = driver_dict[path[path.rindex('.'):]]
            except KeyError as ext:
                print("Bad file type:", ext)
                exit()

            ## Get GDAL layer from path
            driver = ogr.GetDriverByName(driver)
            data_file = driver.Open(path, 0)
            if data_file == None: print("Bad File."); exit()
            ogrlayer = data_file.GetLayer()

            self.name = os.path.splitext(os.path.basename(path))[0] ## (name, ext) #! Maybe move this and use ext
            
            self.from_gdal_layer(ogrlayer)

    def _activate(self, new_parent):
        self.parent = new_parent

        x, y = self.parent.geo2proj(self.x_list, self.y_list)
        self.x_list, self.y_list = list(x), list(y)

    def add_field(self, field_name):
        self.fields.append(field_name)
    
    def new_feature(self):
        new_feature = PointFeature(self)
        self.features.append(new_feature)
        return new_feature

    def set_opacity(self, new_opacity):
        self._alpha = new_opacity

    def __len__(self):
        ## Return number of items in features list
        return len(self.features)

    def __getitem__(self, key):
        return self.features[key]

    def __iter__(self):
        ## Create index for iteration and return self
        self._iter_indx = 0
        return self

    def __next__(self):
        ## If there are no more feature then stop iteration
        if self._iter_indx == len(self.features):
            raise StopIteration

        ## Return next feature from features list
        feature = self.features[self._iter_indx]
        self._iter_indx += 1
        return feature

    def box_select(self, min_x, min_y, max_x, max_y):
        """ Returns features within a given box """
        selected_features = []
        for feature in self.features:
            g_min_x, g_min_y, g_max_x, g_max_y = feature.get_extent()

            if (
                ## Geometry completely or partially within selector 
                ((g_max_x >= min_x and g_min_x <= max_x) and (g_max_y >= min_y and g_min_y <= max_y)) 
                or
                ## Selector completely within geometry
                (g_min_x <= min_x and g_max_x >= max_x and (g_min_y <= min_y and g_max_y >= max_y))):
                    selected_features.append(feature)

        return selected_features

    def point_select(self, proj_x, proj_y):
        """ Selects feature at exact point """
        ## Box select small two pixel sized box into shortlist
        min_x = proj_x - self.parent._proj_scale * 2
        min_y = proj_y - self.parent._proj_scale * 2
        max_x = proj_x + self.parent._proj_scale * 2
        max_y = proj_y + self.parent._proj_scale * 2
        short_list = self.box_select(min_x, min_y, max_x, max_y)

        ## If point is is within feature, added to final list
        selected_features = []
        for feature in short_list:
            if feature.point_within(proj_x, proj_y):
                selected_features.append(feature)
        return selected_features

    def get_extent(self):
        return min(self.x_list), min(self.y_list), max(self.x_list), max(self.y_list)
    
    def focus(self):
        
        min_x, min_y, max_x, max_y = self.get_extent()

        self.parent._projx = (max_x + min_x)/2
        self.parent._projy = (max_y + min_y)/2

        s_x = (max_x - min_x) / self.parent.width
        s_y = (max_y - min_y) / self.parent.height
        new_scale =  max(s_x, s_y)

        ## Get projection crs dict, ignore all warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            crs_dict = self.parent._projection.crs.to_dict()

        ## If units not defined in crs_dict the units are degrees
        if 'units' not in crs_dict:
            ## Convert scale to m/pix from deg
            new_scale = new_scale * 110570

        elif crs_dict['units'] == 'us-ft':
                new_scale = new_scale / 3.28084
        
        else:
            pass ## Is meters :) scale is already in m/pix
    
        new_scale = new_scale * 1.25

        ## Set processed newscale
        self.parent.set_scale(new_scale)

    def draw(self, renderer, cr):
        """ """
        min_x, min_y = self.parent.pix2proj(0,0)
        max_x, max_y = self.parent.pix2proj(self.parent.width, self.parent.height)


        #'''
        ## Only Draw features in view
        for feature in self.box_select(min_x, min_y, max_x, max_y):
            feature.draw(self, renderer, cr)
        '''
        for feature in self.features:
            feature.draw(self, renderer, cr)
        #'''

    def from_gdal_layer(self, gdal_layer):
        """
        """
        ## Extract field names from gdal_layer and add them to new_layer
        attrib_data = gdal_layer.GetLayerDefn()
        field_count = attrib_data.GetFieldCount()
        for i in range(field_count):
            field_data = attrib_data.GetFieldDefn(i)
            self.add_field(field_data.GetName())
    

        for feature in gdal_layer:
            feature_geom = feature.GetGeometryRef()
            feature_class = {"POINT": PointFeature, 
                            "MULTIPOINT": PointFeature,
                            "LINESTRING": LineFeature, 
                            "MULTILINESTRING": LineFeature, 
                            "POLYGON": PolygonFeature,
                            "LINEARRING": PolygonFeature,
                            "MULTIPOLYGON": PolygonFeature}[feature_geom.GetGeometryName()]
            
            new_feature = feature_class(self)
            self.features.append(new_feature)
            new_feature.from_gdal_feature(feature)




