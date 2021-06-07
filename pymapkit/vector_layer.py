"""
Project: PyMapKit
Title: VectorLayer
Function: Holds Classes for Rendering Vector Data
Author: Ben Knisley [benknisley@gmail.com]
Date: 7, November 2020
"""
import os
import math
import bisect
from operator import methodcaller
import pyproj
import ogr
from .base_layer import BaseLayer


class BaseStyle:
    def __init__(self, parent_feature):
        """
        """
        ## Store ref to stylized parent object
        self.feature = parent_feature

        ## Create a dict to hold display modes
        self.display_modes = {'none': ([], [])} # name, (prop list, defaults)

        ## Create a display placeholder
        self.display = 'none'

        ## Create a cached function placeholder
        self.cached_renderer_fn = None

        ## Create empty list to hold current dynamic properties and methods
        self.dynamic_properties = []
        self.dynamic_methods = []

        parent_feature.dependent = False

    def set_display(self, new_display):
        ## Set display value from new_display
        self.display = new_display
        
        ## If new_display is Ellipsis, overwrite new_display value
        if new_display == ...:
            new_display = self.feature.parent.style.display

        ## Get property names & default values from ChildClass.display_modes
        properties, defaults = self.display_modes[new_display]

        ## Copy existing values if property exists in old and new display
        values = []
        for prop, default in zip(properties, defaults):
            if prop in self.dynamic_properties:
                values.append(self.__dict__[prop])
            else:
                values.append(default)

        ## Delete old dynamic properties
        for prop in [p for p in self.dynamic_properties if p not in properties]:
            del self.__dict__[prop]
        self.dynamic_properties = []

        ## Delete old dynamic methods
        for method in self.dynamic_methods:
            del self.feature.__dict__[method]
        self.dynamic_methods = []
        

        ## Define set_display template
        def set_display_templ(self, new_value):
            self.style.set_display(new_value)
        
        def get_display_templ(self):
            return self.style.__dict__['display']

        ## Link, and bind set_display as a named method of the parent feature
        bound_setter = set_display_templ.__get__(self.feature, type(self.feature))
        self.feature.__dict__['set_display'] = bound_setter

        ## Link, and bind set_display as a named method of the parent feature
        bound_getter = get_display_templ.__get__(self.feature, type(self.feature))
        self.feature.__dict__['get_display'] = bound_getter
    

        for prop_name, default in zip(properties, values):


            ## Create the property, and register it with dynamic_properties
            self.feature.style.__dict__[prop_name] = default
            self.dynamic_properties.append(prop_name)

            self.create_property_methods(prop_name, default)

    def create_property_methods(self, prop_name, new_value):

            ## Define a property setter method
            def setter_template(self, new_value):
                if self.dependent: #! NOTE: This is a simple hack. It works, but should be renamed and revised
                    list(map(methodcaller('set_'+prop_name, new_value), self.features))
                    list(map(methodcaller('clear_cache'), self.features))
                    return
                
                self.style.__dict__[prop_name] = new_value
                print('Clearing cached function')
                self.clear_cache()

            ## Define a property getter method
            def getter_template(self):
                return self.style.__dict__[prop_name]
            
            ## Bind setter and getter to parent feature
            bound_setter = setter_template.__get__(self.feature, type(self.feature))
            bound_getter = getter_template.__get__(self.feature, type(self.feature))

            ## Link bound_setter as a named method
            self.feature.__dict__['set_'+prop_name] = bound_setter
            self.feature.__dict__['get_'+prop_name] = bound_getter

            ## Add getter and setter names to dynamic_methods list
            self.dynamic_methods.append('set_'+prop_name)
            self.dynamic_methods.append('get_'+prop_name)

    def __getattribute__(self, item):
        ## Create a passthrough to prevent recursion
        if item == "dynamic_properties":
            return object.__getattribute__(self,item)
  
        
        ## Prepare to override if certain attribute
        if item in self.dynamic_properties + ["display"]:
            ## Get value of attribute
            value = self.__dict__[item]

            ## If attribute value is an Ellipsis, override it
            if value == ...:
                return self.feature.parent.style.__dict__[item]
            else:
                return value
        
        ## Recreate original functionality
        return object.__getattribute__(self,item)

    def add_display_mode(self, mode_name, properties, defaults):
        """
        Creates a new display mode
        
        Creates a new display mode, by adding details to display_modes dict. 
        To be used by a child class to create display modes for specific 
        targets.
        """
        self.display_modes[mode_name] = (properties, defaults)

class PolyStyle(BaseStyle):
    def __init__(self, parent_feature):
        """
        """
        BaseStyle.__init__(self, parent_feature)
        
        self.type = 'polygon'

        self.add_display_mode('basic', ['color', 'outline_color', 'outline_weight', 'opacity', 'outline_opacity'], [..., ..., ..., ..., 1, 1])
        self.add_display_mode('image', ['path', 'outline_color', 'outline_weight', 'opacity', 'outline_opacity'], [..., ..., ..., ..., 1, 1])

        self.set_display('none')



    



class Geometry:
    """
    A class that abstracts a geometry
    """
    def __init__(self, parent):
        self.parent = parent
        self.geometry_type = parent.geometry_type

        self.skip_draw = False
        ##
        self.geom_index = len(parent.geometries)

        self.structure = []
        self.start_address = len(parent.x_values)
        self.length = 0
    
    def add_subgeometry(self, x_points, y_points):
        self.structure.append(len(x_points))
        self.length += len(x_points)
        
        if self == self.parent.geometries[-1]:
            self.parent.x_values += x_points
            self.parent.y_values += y_points
        else:
            #! CHANGE ADDRESS OF ALL FOLLOWING GEOMS IN PARENT
            pass
        

    def get_points(self):
        x_values = self.parent.x_values[self.start_address:self.start_address+self.length]
        y_values = self.parent.y_values[self.start_address:self.start_address+self.length]
        return x_values, y_values

    def subgeometry_count(self):
        return len(self.structure)

    def get_subgeometry(self, index):
        ## Find start address of subgeom in common point list
        init_point = self.start_address + sum(self.structure[:index])
        
        ## Find last point belonging to subgeom in common point list
        geom_size = self.structure[index]
        term_point = init_point + geom_size

        ## Get points from splices of common point sequences
        x_points = self.parent.x_values[init_point:term_point]
        y_points = self.parent.y_values[init_point:term_point]

        ## Return point lists
        return x_points, y_points
    
    def get_subgeometries(self):
        geom_list = []

        ## Add all subgeoms into geom_list
        for i in range(self.subgeometry_count()):
            geom_list.append(self.get_subgeometry(i))
        
        return geom_list

    def get_extent(self):
        x_vals, y_vals = self.get_points()
        return min(x_vals), min(y_vals), max(x_vals), max(y_vals)

    def point_within(self, test_x, test_y):
        if self.geometry_type == 'point':
            for x_points, y_points in self.get_subgeometries():
                for point_x, point_y in zip(x_points, y_points):
                    if(math.isclose(test_x, point_x, abs_tol=self.parent.map._proj_scale*5) and
                        math.isclose(test_y, point_y, abs_tol=self.parent.map._proj_scale*5)):
                        return True
            return False
        elif self.geometry_type == 'line':
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
                            pix_dist = dist / self.parent.map._proj_scale

                            ## If distance is less than 10 pixels, then point is near enough
                            if pix_dist < 10:
                                return True
                    ## Increment last point
                    x1,y1 = x2,y2 
            return False
        else: ## geom_type == polygon
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

class Feature:
    """
    A class representing a single feature
    """
    def __init__(self, parent, geometry):
        self.parent = parent
        self.geometry = geometry

        self.style = PolyStyle(self)
        self.style.set_display(...)
        #self.style.set_defaults(parent.geometry_type)

        self.attributes = {}
        for field in parent.field_names:
            self.attributes[field] = None

    def __getitem__(self, field_name):
        return self.attributes[field_name]

    def __setitem__(self, field_name, value):
        self.attributes[field_name] = value

    def clear_cache(self):
        self.style.cached_renderer_fn = None

    ## 
    def focus(self):
        """
        """
        ## If layer is not activated, raise Exception
        if self.parent.map == None:
            raise Exception("Layer is not activated.")
        
        ## Get layer extent
        min_x, min_y, max_x, max_y = self.geometry.get_extent()

        ## Calculate center and set new map coord 
        proj_x = (max_x + min_x) / 2
        proj_y = (max_y + min_y) / 2
        self.parent.map.set_projection_coordinates(proj_x, proj_y)

        ## If layer has no area (i.e. is a point), do not proceed 
        if (max_x - min_x) == 0 or (max_y - min_y) == 0:
            return

        ## Calculate best scale for layer
        s_x = (max_x - min_x) / self.parent.map.width
        s_y = (max_y - min_y) / self.parent.map.height
        new_scale = max(s_x, s_y)

        ## Scale out a bit
        new_scale = new_scale * 1.25

        ## Set newscale
        self.parent.map.set_scale(new_scale, True)

class FeatureList:
    """
    Hold a subset of features stored in parent VectorLayer
    """
    def __init__(self, parent, features):
        self.parent = parent
        self.features = features

        self.style = PolyStyle(self)
        self.style.set_display(parent.get_display())

        self.dependent = True
    
    def clear_cache(self):
        for feature in self.features:
            feature.style.cached_renderer_fn = None

    
    def __len__(self):
        return len(self.features)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.features[key]
        else: 
            return FeatureDict(self, key)
    
    def __repr__(self):
        repr_string = f"(dependent) {self.parent.geometry_type.capitalize()} feature list with {len(self)} features."
        return repr_string
    
    def __iter__(self):
        self._iter_index = 0
        return self

    def __next__(self):
        if self._iter_index == len(self.features):
            raise StopIteration
        retn = self.features[self._iter_index]
        self._iter_index += 1
        return retn
    
    def to_new_layer(self):
        new_layer = VectorLayer(self.parent.geometry_type, self.parent.field_names)
        for f in self.features:
            new_layer.add(f)
        
        new_layer.geo_x_values, new_layer.geo_y_values = self.parent.map.proj2geo(new_layer.x_values, new_layer.y_values)

        return new_layer

    def run_on_all(self, method_name, *args):
        has_return = False
        rtrn_list = []
        for rtrn in map(methodcaller(method_name, *args), self.features):
            has_return = has_return or bool(rtrn)
            rtrn_list.append(rtrn)

class FeatureDict:
    """
    Holds a subset of labeled features stored in parent VectorLayer
    """
    def __init__(self, parent, field):
        self.parent = parent
        self.field = field
        self.keys = []
        self.features = []

        self.style = PolyStyle(self)
        self.style.set_display(parent.get_display())

        for feature in self.parent.features:
            self.features.append(feature)
            self.keys.append(feature[self.field])
    
    def clear_cache(self):
        for feature in self.features:
            #feature.style.cached_renderer = None
            feature.style.cached_renderer_fn = None


    def __getitem__(self, compair):
        return_features = []

        ## Equal to
        if not isinstance(compair, slice):
            for value, feature in zip(self.keys, self.features):
                if value == compair:
                    return_features.append(feature)
            
            ##
            if len(return_features) == 0:
                return None
            elif len(return_features) == 1:
                return return_features[0]

        ## Compair
        else:
            for value, feature in zip(self.keys, self.features):
                if (not bool(compair.start) or (value > compair.start)) and (not bool(compair.stop) or (value < compair.stop)):
                    return_features.append(feature)

        ##
        new_feature_list = FeatureList(self.parent, return_features)

        return new_feature_list
    
    def __iter__(self):
        self._iter_index = 0
        return self

    def __next__(self):
        if self._iter_index == len(self.keys):
            raise StopIteration
        key = self.keys[self._iter_index]
        self._iter_index += 1
        return key

    def __repr__(self):
        return str(self.keys)
    
    ## 
    def __eq__(self, compare):
        retn_list = []
        for field, feature in zip(self.keys, self.features):
            if field == compare:
                retn_list.append(feature)
        return FeatureList(self.parent, retn_list)
    
    def __ne__(self, compare):
        retn_list = []
        for field, feature in zip(self.keys, self.features):
            if field != compare:
                retn_list.append(feature)
        return FeatureList(self.parent, retn_list)

    def __lt__(self, compare):
        retn_list = []
        for field, feature in zip(self.keys, self.features):
            if field < compare:
                retn_list.append(feature)
        return FeatureList(self.parent, retn_list)
    
    def __gt__(self, compare):
        retn_list = []
        for field, feature in zip(self.keys, self.features):
            if field > compare:
                retn_list.append(feature)
        return FeatureList(self.parent, retn_list)

    def __le__(self, compare):
        retn_list = []
        for field, feature in zip(self.keys, self.features):
            if field <= compare:
                retn_list.append(feature)
        return FeatureList(self.parent, retn_list)

    def __ge__(self, compare):
        retn_list = []
        for field, feature in zip(self.keys, self.features):
            if field >= compare:
                retn_list.append(feature)
        return FeatureList(self.parent, retn_list)

class VectorLayer(BaseLayer):
    """ """
    def __init__(self, geometry_type, field_names):
        ## Init base layer parent
        BaseLayer.__init__(self)

        ## Set name and update status
        self.status = 'initializing'
        self.name = 'Vector Layer'

        self.field_names = field_names
        self.features = []


        ## Style 
        self.style = PolyStyle(self)
        self.set_display('basic')

        ##
        self.set_color('green')
        self.set_outline_color('black')
        self.set_outline_weight(2)
        self.set_opacity(1)
        



        ## >> self.projection = pyproj.Proj(projection)
        self.geographic_crs = pyproj.crs.CRS("EPSG:4326")

        self.geometry_type = geometry_type
        self.geometries = []

        ## Hold geo values as reference
        self.geo_x_values = []
        self.geo_y_values = []

        ## Projected values
        self.x_values = []
        self.y_values = []

        ## Setup variables for fast sorting
        self.view_sort = True
        self.extents_sorted = False
        self.maxx = []
        self.maxy = []
        self.minx = []
        self.miny = []

        ## Update status
        self.status = 'initialized'

    def __repr__(self):
        """ Returns a string representation of the VectorLayer """
        return f"{self.geometry_type.capitalize()} VectorLayer with {len(self)} features."
    
    def __add__(self, other):
        """ Implement add (+) operator """
        new_set = VectorLayer(self.geometry_type, self.field_names)
        
        for feature in self:
            new_set.add(feature)
        
        for feature in other:
            new_set.add(feature)

        return new_set

    def __len__(self):
        """ Returns the number of features stored in layer."""
        return len(self.features)

    def __getitem__(self, key):
        """ Returns a feature or a FeatureDict based on given key """
        if isinstance(key, int):
            return self.features[key]
        else: 
            return FeatureDict(self, key)

    def activate(self):
        """
        """
        self.status = 'loading'

        self.x_values, self.y_values = self.map.geo2proj(self.geo_x_values, self.geo_y_values)
        self.extents_sorted = False
        self.maxx = []
        self.maxy = []
        self.minx = []
        self.miny = []

        self.status = 'ready'

    def deactivate(self):
        ## Update status
        self.status = 'initialized'



    def clear_cache(self):
        for feature in self.features:
            #feature.style.cached_renderer = None
            feature.style.cached_renderer_fn = None



    def new(self):
        """
        Creates a new feature inside FeatureSet
        """
        #! ADD A PROJECTION CHECK & FIELDS CHECK

        new_geom = Geometry(self)
        self.geometries.append(new_geom)

        new_feature = Feature(self, new_geom)
        self.features.append(new_feature)

        return new_feature

    def add(self, old_feature):
        """
        Adds an existing feature inside FeatureSet
        """
        new_geom = Geometry(self)
        self.geometries.append(new_geom)

        new_feature = Feature(self, new_geom)
        self.features.append(new_feature)

        new_geom.structure = old_feature.geometry.structure.copy()

        x_values, y_values = old_feature.geometry.get_points()
        new_geom.length = len(x_values)
        self.x_values += x_values
        self.y_values += y_values

        for field_name in self.field_names:
            new_feature[field_name] = old_feature[field_name]

        return new_feature

    def get_extent(self):
        return min(self.x_values), min(self.y_values), max(self.x_values), max(self.y_values)

    def box_select(self, min_x, min_y, max_x, max_y):
        ## Create return list
        selected_features = []

        ## Loop through all features in layer, adding them to return list 
        ## if within selection box
        for feature in self.features:
            g_min_x, g_min_y, g_max_x, g_max_y = feature.geometry.get_extent()

            if (
                ## Geometry completely or partially within selector 
                ((g_max_x >= min_x and g_min_x <= max_x) and (g_max_y >= min_y and g_min_y <= max_y)) 
                or
                ## Selector completely within geometry
                (g_min_x <= min_x and g_max_x >= max_x and (g_min_y <= min_y and g_max_y >= max_y))):
                    selected_features.append(feature)

        return FeatureList(self, selected_features)

    def point_select(self, proj_x, proj_y):
        ## Box select small two pixel sized box into shortlist
        min_x = proj_x - self.map._proj_scale * 2
        max_x = proj_x + self.map._proj_scale * 2
        min_y = proj_y - self.map._proj_scale * 2
        max_y = proj_y + self.map._proj_scale * 2

        short_list = self.box_select(min_x, min_y, max_x, max_y)

        ## If point is is within feature, added to final list
        selected_features = []
        for feature in short_list:
            if feature.geometry.point_within(proj_x, proj_y):
                selected_features.append(feature)
        
        return FeatureList(self, selected_features)
   
    def run_on_all(self, method_name, *args):
        has_return = False
        rtrn_list = []
        for rtrn in map(methodcaller(method_name, *args), self.features):
            has_return = has_return or bool(rtrn)
            rtrn_list.append(rtrn)
    
    """ Methods for viewport based rendering """

    def sort_extents(self):
        """
        """
        print("Sorting")
        self.maxx = []
        self.minx = []
        self.maxy = []
        self.miny = []

        for geom in self.geometries:
            mnx, mny, mxx, mxy = geom.get_extent()
            self.maxx.append( (mxx, geom ) )
            self.minx.append( (mnx, geom ) )
            self.maxy.append( (mxy, geom ) )
            self.miny.append( (mny, geom ) )

        self.maxx.sort(key=lambda x: x[0])
        self.minx.sort(key=lambda x: x[0])
        self.maxy.sort(key=lambda x: x[0])
        self.miny.sort(key=lambda x: x[0])

        self.extents_sorted = True

    def mark_visible(self):
        """
        """
        for geom in self.geometries:
            geom.skip_draw = False

        xs, ys = self.map.pix2proj([0, self.map.width], [0, self.map.height])
        minx, maxx = xs 
        miny, maxy = ys

        ind = bisect.bisect_left([i[0] for i in self.minx], maxx)
        for _, geom in self.minx[ind:]:
            geom.skip_draw = True
        
        ind = bisect.bisect_left([i[0] for i in self.maxx], minx)
        for _, geom in self.maxx[:ind]:
            geom.skip_draw = True
    
        ind = bisect.bisect_left([i[0] for i in self.miny], maxy)
        for _, geom in self.miny[ind:]:
            geom.skip_draw = True
        
        ind = bisect.bisect_left([i[0] for i in self.maxy], miny)
        for _, geom in self.maxy[:ind]:
            geom.skip_draw = True
        

    def render(self, renderer, canvas):
        """
        """
        ## Update Status
        self.status = 'rendering'

        if self.view_sort:
            if not self.extents_sorted:
                self.sort_extents()
            self.mark_visible()
            
        if self.geometry_type == 'polygon':
            for feature in self.features:

                if feature.geometry.skip_draw:
                    continue
                
                #if not feature.style.cached_renderer: 
                #    feature.style.cache_renderer(renderer)
                
                pix_x, pix_y = self.map.proj2pix(*feature.geometry.get_points())
                renderer.draw_polygon(canvas, feature.geometry.structure, pix_x, pix_y, feature.style)
        
        elif self.geometry_type == 'line':
            for feature in self.features:
                
                if feature.geometry.skip_draw:
                    continue

                if not feature.style.cached_renderer: 
                    feature.style.cache_renderer(renderer)
                
                pix_x, pix_y = self.map.proj2pix(*feature.geometry.get_points())
                renderer.draw_line(canvas, feature.geometry.structure, pix_x, pix_y, feature.style)
        
        elif self.geometry_type == 'point':
            for feature in self.features:
            
                if feature.geometry.skip_draw:
                    continue

                if not feature.style.cached_renderer: 
                    feature.style.cache_renderer(renderer)
                
                pix_x, pix_y = self.map.proj2pix(*feature.geometry.get_points())
                renderer.draw_point(canvas, feature.geometry.structure, pix_x, pix_y, feature.style)
        
        else:
            pass

        ## Update Status
        self.status = 'rendered'

    """ Extra Constructors """

    @classmethod
    def from_path(cls, path):
        ## Load Gdal from file extension
        driver_dict = {'.shp': 'ESRI Shapefile', '.geojson': 'GeoJSON'}
        try:
            driver = driver_dict[path[path.rindex('.'):]]
        except KeyError as ext:
            print("Bad file type:", ext)
            return

        ## Get GDAL layer from path
        driver = ogr.GetDriverByName(driver)
        data_file = driver.Open(path, 0)
        if data_file == None: print("Bad File."); return
        ogrlayer = data_file.GetLayer()
        
        rtrn_layer = VectorLayer.from_gdal_layer(ogrlayer)

        rtrn_layer.name = os.path.basename(path)

        return rtrn_layer

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
        
        ## Create VectorLayer to hold features
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
            
        new_layer.geo_x_values = new_layer.x_values
        new_layer.geo_y_values = new_layer.y_values

        return new_layer