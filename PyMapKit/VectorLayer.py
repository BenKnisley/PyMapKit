"""
Project: PyMapKit
Title: VectorLayer
Function: Holds Classes for Rendering Vector Data
Author: Ben Knisley [benknisley@gmail.com]
Created: 20 July, 2020
"""
import warnings
from operator import methodcaller
import pyproj

from .VectorFeatures import FeatureHost, FeatureList, FeatureDict, Geometry
from .VectorFeatures import Feature as _Feature

class FeatureStyle:
    def __init__(self):
        self.cached_renderer = None
        
        self.display = None

        self.color = 'green'
        self._color_cache = None
        self.opacity = 1

        self.outline_color = 'black'
        self._outline_color_cache = None

        self.weight = 1
        self.outline_weight = 1
    
    def set_defaults(self, geometry_type):
        if geometry_type == 'point':
            self.display = 'point'
            self.color = 'red'
            self.weight = 3
            self.outline_color = 'black'
            self.outline_weight = 1
        
        elif geometry_type == 'line':
            self.display = 'solid'
            self.color = 'blue'
            self.weight = 0.5
            self.outline_color = 'black'
            self.outline_weight = 0
        
        else: ## geometry_type == Polygon
            self.display = 'solid'
            self.color = 'green'
            self.weight = 1
            self.outline_color = 'black'
            self.outline_weight = 1
        
    
    def cache_renderer(self, renderer):
        self._color_cache = renderer.cache_color(self.color, opacity=self.opacity)
        self._outline_color_cache = renderer.cache_color(self.outline_color, opacity=self.opacity)
        self.cached_renderer = renderer
    
    def set_color(self, new_color):
        self.color = new_color
        self._color_cache = None
        self.cached_renderer = None
    
    def set_outline_color(self, new_color):
        self.outline_color = new_color
        self._outline_color_cache = None
        self.cached_renderer = None

class Feature(_Feature):
    def __init__(self, parent, attributes_names, geometry):
        _Feature.__init__(self, attributes_names, geometry)
        self.parent = parent
        self.style = FeatureStyle()
        self.style.set_defaults(parent.geometry_type)
    
    def set_color(self, color):
        self.style.set_color(color)

    def set_outline_color(self, new_color):
        self.style.set_outline_color(new_color)
    
    def set_weight(self, new_weight):
        self.style.weight = new_weight

    def set_outline_weight(self, new_weight):
        self.style.outline_weight = new_weight

    def focus(self):
        min_x, min_y, max_x, max_y = self.geometry.get_extent()

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

class VectorLayer(FeatureHost):
    def __init__(self, geometry_type, field_names):
        FeatureHost.__init__(self, geometry_type, field_names, projection="EPSG:4326")
        self.parent = None

    def new(self):
        new_geom = Geometry(self, self.geometry_type)
        self.geometries.append(new_geom)

        new_feature = Feature(self, self.field_names, new_geom)
        self.features.append(new_feature)

        return new_feature

    def add(self, old_feature):
        new_feature = super().add(old_feature)
        new_style = FeatureStyle()
        new_feature.style = new_style
        new_feature.parent = self
        return new_feature


    def _activate(self, parent):
        self.parent = parent

        ## Make sure projection matches
        if self.projection != self.parent._projection:
            x_vals, y_vals = pyproj.transform(self.projection, self.parent._projection, self.y_values, self.x_values)
            self.x_values, self.y_values = x_vals, y_vals

            self.projection = self.parent._projection
    
    def draw(self, renderer, cr):
        if self.geometry_type == 'polygon':
            for feature in self:
                
                if not feature.style.cached_renderer: 
                    feature.style.cache_renderer(renderer)
                
                pix_x, pix_y = self.parent.proj2pix(*feature.geometry.get_points())
                renderer.draw_polygon(cr, feature.geometry.structure, pix_x, pix_y, feature.style)
        
        elif self.geometry_type == 'line':
            for feature in self:
                
                if not feature.style.cached_renderer: 
                    feature.style.cache_renderer(renderer)
                
                pix_x, pix_y = self.parent.proj2pix(*feature.geometry.get_points())
                renderer.draw_line(cr, feature.geometry.structure, pix_x, pix_y, feature.style)
        
        elif self.geometry_type == 'point':
            for feature in self:

                if not feature.style.cached_renderer: 
                    feature.style.cache_renderer(renderer)
                
                pix_x, pix_y = self.parent.proj2pix(*feature.geometry.get_points())
                renderer.draw_point(cr, feature.geometry.structure, pix_x, pix_y, feature.style)
        
        else:
            pass

    def focus(self):
        min_x, min_y, max_x, max_y = self.get_extent()

        self.parent._projx = (max_x + min_x)/2
        self.parent._projy = (max_y + min_y)/2

        if (max_x - min_x) == 0 or (max_y - min_y) == 0:
            return

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


    def get_extent(self):
        return min(self.x_values), min(self.y_values), max(self.x_values), max(self.y_values)

    def run_on_all(self, method_name, *args):
        has_return = False
        rtrn_list = []
        for rtrn in map(methodcaller(method_name, *args), self.features):
            has_return = has_return or bool(rtrn)
            rtrn_list.append(rtrn)

    def point_select(self, proj_x, proj_y):
        ## Box select small two pixel sized box into shortlist
        min_x = proj_x - self.parent._proj_scale * 2
        max_x = proj_x + self.parent._proj_scale * 2
        min_y = proj_y - self.parent._proj_scale * 2
        max_y = proj_y + self.parent._proj_scale * 2

        short_list = self.box_select(min_x, min_y, max_x, max_y)

        ## If point is is within feature, added to final list
        selected_features = []
        for feature in short_list:
            if feature.geometry.point_within(proj_x, proj_y):
                selected_features.append(feature)
        
        return FeatureList(self, selected_features)
    
    @classmethod
    def from_gdal_layer(cls, gdal_layer):
        ## Get scheme from layer, load into field_names
        field_names = []
        layer_def = gdal_layer.GetLayerDefn()
        for i in range(layer_def.GetFieldCount()):
            field_def = layer_def.GetFieldDefn(i)
            field_names.append(field_def.GetName())
        
        ## Find geometry type of layer
        test_feature = gdal_layer.GetNextFeature()
        geometry = test_feature.GetGeometryRef()
        geom_type = geometry.GetGeometryName()
        gdal_layer.ResetReading()

        #! DO SOMETHING ABOUT PROJECTION
        
        ## Create VectorSet to hold features
        geometry_type = {"POLYGON":"polygon", "LINEARRING":"polygon", "MULTIPOLYGON":"polygon", "LINESTRING":"line", "MULTILINESTRING":"line", "POINT":"point", "MULTIPOINT":"point"}[geom_type]
        new_layer = VectorLayer(geometry_type, field_names)

        ## If polygon
        if geom_type in ("POLYGON", "LINEARRING", "MULTIPOLYGON"):
            for feature in gdal_layer:
                ## Create a new Feature, & extract new_geom from new_feature
                new_feature = new_layer.new()
                new_geom = new_feature.geometry

                ## Load fields from GDAL feature into new feature
                for field_name in field_names:
                    new_feature[field_name] = feature[field_name]
                
                ## Load all subgeometry into  new_layer geom
                geom = feature.GetGeometryRef()
                for indx in range(geom.GetGeometryCount()):
                    subpoly_geom = geom.GetGeometryRef(indx)

                    ## Account for weird GDAL subgeom thing
                    if subpoly_geom.GetGeometryName() == "POLYGON":
                        subpoly_geom = subpoly_geom.GetGeometryRef(0)

                    ## Load points from subgeom into lists
                    x_coord_list, y_coord_list = [], [] 
                    for point in subpoly_geom.GetPoints():
                        x_coord_list.append(point[0])
                        y_coord_list.append(point[1])
                    
                    ## Create new subgeom
                    new_geom.add_subgeometry(x_coord_list, y_coord_list)

        elif geom_type in ("LINESTRING", "MULTILINESTRING"):
            for feature in gdal_layer:
                ## Create a new Feature, & extract new_geom from new_feature
                new_feature = new_layer.new()
                new_geom = new_feature.geometry

                ## Load fields from GDAL feature into new feature
                for field_name in field_names:
                    new_feature[field_name] = feature[field_name]
                
                ## Load all subgeometry into new features geom
                geom = feature.GetGeometryRef()
                geocount = geom.GetGeometryCount()
                if geocount == 0:
                    x_list, y_list = [], []
                    for point in geom.GetPoints():
                        x_list.append(point[0])
                        y_list.append(point[1])
                    new_geom.add_subgeometry(x_list, y_list)
                else:
                    for indx in range(geom.GetGeometryCount()):
                        subgeom = geom.GetGeometryRef(indx)
                        
                        x_list, y_list = [], []
                        for point in subgeom.GetPoints():
                            x_list.append(point[0])
                            y_list.append(point[1])
                        new_geom.add_subgeometry(x_list, y_list)



        elif geom_type in ("POINT", "MULTIPOINT"):
            for feature in gdal_layer:
                ## Create a new Feature, & extract new_geom from new_feature
                new_feature = new_layer.new()
                new_geom = new_feature.geometry

                ## Load fields from GDAL feature into new feature
                for field_name in field_names:
                    new_feature[field_name] = feature[field_name]
                
                ## Load all subgeometry into new features geom
                geom = feature.GetGeometryRef()
                if geom.GetGeometryCount() == 0:
                    x_list, y_list = [], []
                    for point in geom.GetPoints():
                        x_list.append(point[0])
                        y_list.append(point[1])
                    new_geom.add_subgeometry(x_list, y_list)
                
                ## Mutipoint
                else:
                    for indx in range(geom.GetGeometryCount()):
                        subpoly_geom = geom.GetGeometryRef(indx)

                        x_list, y_list = [], []
                        for point in subpoly_geom.GetPoints():
                            x_list.append(point[0])
                            y_list.append(point[1])
                        new_geom.add_subgeometry(x_list, y_list)
        else:
            pass

        return new_layer
