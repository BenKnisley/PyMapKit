#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Created: 20 July, 2020
"""
import ogr
import numpy as np
import warnings


class VectorFeature:
    def __init__(self, parent):
        self.parent = parent
        self.attribute_dict = {}

        self.init_address = len(self.parent.x_list)
        self.point_count = 0
        self.geom_struct = []
    
    def set_attributes(self, attributes):
        for field_name, attribute in zip(self.parent.fields, attributes):
            self.attribute_dict[field_name] = attribute
    
    def __getitem__(self, key):
        if isinstance(key, str):
            key = self.parent.fields.index(key)
            return self._attributes[key]
        
    def from_gdal_feature(self, feature):
        for field in self.parent.fields:
            self.attribute_dict[field] = feature.GetField(field)

        geom = feature.GetGeometryRef()
            
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
        self.point_count += len(new_x_points)
        #self.geom_struct.append( (len(self.parent.x_list), len(new_x_points)) )
        self.geom_struct.append(len(new_x_points))
        self.parent.x_list += new_x_points
        self.parent.y_list += new_y_points

    def subgeometry_count(self):
        return len(self.geom_struct)
    
    def get_subgeometry(self, index):
        init_point = sum(self.geom_struct[:index])
        geom_size = self.geom_struct[index]
        term_point = init_point + geom_size
        x_points = self.parent.x_list[init_point:term_point]
        y_points = self.parent.y_list[init_point:term_point]
        return x_points, y_points

    def get_subgeometries(self):
        for i in range(self.subgeometry_count()):
            yield self.get_subgeometry(i)

    def get_points(self):
        x_points = self.parent.x_list[self.init_address:self.init_address+self.point_count]
        y_points = self.parent.y_list[self.init_address:self.init_address+self.point_count]
        return x_points, y_points

    def get_extent(self):
        x_points, y_points = self.get_points()
        return min(x_points), min(y_points), max(x_points), max(y_points)

class PointFeature(VectorFeature):
    """ """
    def __init__(self, parent):
        """ """
        VectorFeature.__init__(self, parent)
        self._color = 'green' ## Default color is green
        self._cached_color = None
        self._radius = 2

    def set_color(self, input_color):
        """ """
        self._color = input_color
        self._cached_color = None

    def set_size(self, input):
        self._radius = input / 2

    def draw(self, layer, renderer, cr):
        ## If color not cached yet, cache it
        if self._cached_color == None:
            self._cached_color = renderer.color_converter(self._color)

        ## Calculate pixel values
        pix_x, pix_y = layer.parent.proj2pix(*self.get_points())

        ## Draw point
        renderer.draw_point(cr, self.geom_struct, pix_x, pix_y, self._cached_color, self._radius, layer._alpha)

class LineFeature(VectorFeature):
    """ """
    def __init__(self, parent):
        """ """
        VectorFeature.__init__(self, parent)
        self._color = 'red' ## Default color is green
        self._cached_color = None

        self._width = 1

    def set_color(self, input_color):
        """ """
        self._color = input_color
        self._cached_color = None

    def set_size(self, input_width):
        """ """
        self._width = input_width

    def draw(self, layer, renderer, cr):
        ## If color not cached yet, cache it
        if self._cached_color == None:
            self._cached_color = renderer.color_converter(self._color)

        ## Calculate pixel values
        pix_x, pix_y = layer.parent.proj2pix(*self.get_points())
        renderer.draw_line(cr, self.geom_struct, pix_x, pix_y, self._width, self._cached_color, layer._alpha)

class PolygonFeature(VectorFeature):
    """ """
    def __init__(self, parent):
        """ """
        VectorFeature.__init__(self, parent)
        self._bgcolor = "blue"
        self._cached_bgcolor = None
        self._line_color = "black"
        self._cached_line_color = None
       
        self._line_width = 1

    def set_color(self, input_color):
        """ """
        self._bgcolor = input_color
        self._cached_bgcolor = None
        

    def set_line_color(self, input_color):
        """ """
        self._line_color = input_color
        self._cached_line_color = None


    def set_line_width(self, input_width):
        """ """
        self._line_width = input_width

    def draw(self, layer, renderer, cr):
        """ """
        if self._cached_line_color == None:
            self._cached_line_color = renderer.color_converter(self._line_color)

        if self._cached_bgcolor == None:
            self._cached_bgcolor = renderer.color_converter(self._bgcolor)

        ## Calculate pixel values
        #""" ## Full layer vectorization proj2pix optimization
        #pix_x, pix_y = self._pix_x, self. _pix_y
        """ ## Single Vector iteration proj2pix
        pix_x, pix_y = layer.parent.proj2pix(self._proj_x, self._proj_y)
        #"""

        ## Calculate pixel values
        pix_x, pix_y = layer.parent.proj2pix(*self.get_points())
        
        ## Call on renderer to render polygon
        renderer.draw_polygon(cr, self.geom_struct, pix_x, pix_y, self._cached_bgcolor, self._line_width, self._cached_line_color, layer._alpha)

class VectorLayer:
    def __init__(self, path=None):
        self.parent = None
        self._alpha = 1

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
        for geometry in self.features:
            g_min_x, g_min_y, g_max_x, g_max_y = geometry.get_extent()

            if (
                ## Geometry completely or partially within selector 
                ((g_max_x >= min_x and g_min_x <= max_x) and (g_max_y >= min_y and g_min_y <= max_y)) 
                or
                ## Selector completely within geometry
                (g_min_x <= min_x and g_max_x >= max_x and (g_min_y <= min_y and g_max_y >= max_y))
                ):
                yield geometry

    def point_select(self, x, y):
        return self.box_select(x,y,x,y)

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
        for feature in self.features:
            feature.draw(self, renderer, cr)


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




