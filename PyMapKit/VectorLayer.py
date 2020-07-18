"""
Project: PyMapKit
Title: Vector Layer
Function: Provides a class that can display vector based geospatial data.
Author: Ben Knisley [benknisley@gmail.com]
Created: 8 February, 2020
"""
import warnings
from osgeo import ogr
import numpy as np


class _VectorFeature:
    """ """
    def __init__(self):
        """ """
        self._field_list = []
        self._attributes = []

        ## List to hold geom structure tree
        self._geom_struct = np.array([])

        ## NumPy arrays to hold geo coords
        self._geo_x = np.array([])
        self._geo_y = np.array([])

        ## NumPy arrays to hold projection coords
        self._proj_x = np.array([])
        self._proj_y = np.array([])

    def __len__(self):
        return len(self._geo_x)

    def __getitem__(self, key):
        if isinstance(key, str):
            key = self._field_list.index(key)
        return self._attributes[key]

    def _activate(self, MapLayer_obj):
        self._field_list = MapLayer_obj._field_list.copy()

    def _deactivate(self):
        pass

    def get_extent(self):
        pass

    def import_geographic(self, xvalues, yvalues):
        self._geo_x = np.array(xvalues)
        self._geo_y = np.array(yvalues)

class _PointFeature(_VectorFeature):
    """ """
    def __init__(self):
        """ """
        self._color = 'green' ## Default color is green
        self._cached_color = None
        self._radius = 2

    #! TODO: Add a set icon function, to draw image instead of plain circle

    def set_color(self, input_color):
        """ """
        ## Change color and reset _cached_color
        self._color = input_color
        self._cached_color = None

    def set_size(self, input):
        self._radius = input / 2

    def draw(self, layer, renderer, cr):
        ## If color not cached yet, cache it
        if self._cached_color == None:
            self._cached_color = renderer.color_converter(self._color)

        ## Calculate pixel values
        pix_x, pix_y = layer.parent.proj2pix(self._proj_x, self._proj_y)

        ## Draw point
        renderer.draw_point(cr, self._geom_struct, pix_x, pix_y, self._cached_color, self._radius, layer._alpha)

class _LineFeature(_VectorFeature):
    """ """
    def __init__(self):
        """ """
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
        pix_x, pix_y = layer.parent.proj2pix(self._proj_x, self._proj_y)
        renderer.draw_line(cr, self._geom_struct, pix_x, pix_y, self._width, self._cached_color, layer._alpha)

class _PolygonFeature(_VectorFeature):
    """ """
    def __init__(self):
        """ """
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
        pix_x, pix_y = self._pix_x, self. _pix_y
        """ ## Single Vector iteration proj2pix
        pix_x, pix_y = layer.parent.proj2pix(self._proj_x, self._proj_y)
        #"""

        ## Call on renderer to render polygon
        renderer.draw_polygon(cr, self._geom_struct, pix_x, pix_y, self._cached_bgcolor, self._line_width, self._cached_line_color, layer._alpha)

class VectorLayer:
    """
    """

    def __init__(self, path=None):
        """ """
        ## Create placeholder for parent map obj
        self.parent = None

        self._field_list = []
        
        self._focus_point = (0,0)
        self._extent = (0,0,0,0)
        
        self._features = []
        self._alpha = 1

        ## If path is None (default), return empty VectorLayer
        if path == None:
            return
        
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

        ## Get data from ogrlayer, and set layer attributes 
        fields, features = _data_from_OGR_layer(ogrlayer)
        self._load_data(fields, features)
        
    def _load_data(self, field_names, features):
        """
        """
        self._field_list = field_names
        for feature in features:
            feature._activate(self)
            self._features.append(feature)


    def need_redrawn(self):
        return False

    def __len__(self):
        ## Return number of items in features list
        return len(self._features)

    def __getitem__(self, key):
        return self._features[key]

    def __iter__(self):
        ## Create index for iteration and return self
        self._iter_indx = 0
        return self

    def __next__(self):
        ## If there are no more feature then stop iteration
        if self._iter_indx == len(self._features):
            raise StopIteration

        ## Return next feature from features list
        feature = self._features[self._iter_indx]
        self._iter_indx += 1
        return feature

    def _activate(self, new_parent_map):
        """ Function called by Map object when layer is added to itself."""
        self.parent = new_parent_map
        self._project_features()

    def _deactivate(self):
        """ Function called when layer is removed from Map object """
        pass
        
    def focus(self):
        """ """
        self.parent._projx, self.parent._projy = self._focus_point
        s_x = (self._extent[1] - self._extent[0]) / self.parent.width
        s_y = (self._extent[3] - self._extent[2]) / self.parent.height
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




    def _project_features(self):
        ## 
        if len(self._features) == 0:
            return

        ## Clear existing projection lists
        for feature in self._features:
            feature._proj_x = np.array([])
            feature._proj_y = np.array([])

        feature_len_list = []
        grand_geo_point_x_list = []
        grand_geo_point_y_list = []

        ## Add all points from each feature to grand point lists
        for feature in self._features:
            feature_len_list.append(len(feature))
            grand_geo_point_x_list.extend(feature._geo_x)
            grand_geo_point_y_list.extend(feature._geo_y)

        ## Convert grand point lists to Numpy Arrays
        grand_geo_point_x_list = np.array(grand_geo_point_x_list)
        grand_geo_point_y_list = np.array(grand_geo_point_y_list)
        
        ## Project grand point lists
        grand_proj_point_x_list, grand_proj_point_y_list = self.parent.geo2proj(grand_geo_point_y_list, grand_geo_point_x_list)

        ## Get layer extents and focus point
        self._extent = (np.amin(grand_proj_point_x_list), 
                        np.amax(grand_proj_point_x_list),
                        np.amin(grand_proj_point_y_list), 
                        np.amax(grand_proj_point_y_list))

        cent_x = (self._extent[0] + self._extent[1])/2
        cent_y = (self._extent[2] + self._extent[3])/2

        self._focus_point = (cent_x, cent_y)

        self._feature_len_cache = np.array(feature_len_list)
        self._proj_x_cache = grand_proj_point_x_list.copy()
        self._proj_y_cache = grand_proj_point_y_list.copy()

        pointer = 0
        for feature, p_count in zip(self._features, feature_len_list):
            feature._proj_x = grand_proj_point_x_list[pointer:pointer+p_count]
            feature._proj_y = grand_proj_point_y_list[pointer:pointer+p_count]
            pointer += p_count

    def _pixilize_points(self):
        if len(self._features) == 0:
            return

        self._pix_x_cache, self._pix_y_cache = self.parent.proj2pix(self._proj_x_cache, self._proj_y_cache)

        pointer = 0
        for feature, lenght in zip(self._features, self._feature_len_cache):
            feature._pix_x = list( self._pix_x_cache[pointer:pointer+lenght] ) ## Better performance from python list
            feature._pix_y = list( self._pix_y_cache[pointer:pointer+lenght] ) ## Better performance from python list
            pointer += lenght

    def set_opacity(self, opacity_val):
        """ """
        self._alpha = opacity_val
    
    def get_opacity(self):
        """ """
        return self._alpha

    def draw(self, renderer, cr):
        """ """
        self._pixilize_points()
        for feature in self._features:
            feature.draw(self, renderer, cr)


    @staticmethod
    def from_gdal_layer(gdal_layer):
        ## Get data from ogrlayer, and return new VectorLayer
        fields, features = _data_from_OGR_layer(gdal_layer)

        new_lay = VectorLayer(None)
        new_lay._load_data(fields, features)
        return new_lay


    @staticmethod
    def from_shapefile(path):
        ## Setup driver for shapefile, open shapefile
        driver = ogr.GetDriverByName('ESRI Shapefile')
        shapefile = driver.Open(path, 0)

        ## Test if file is readable
        if shapefile == None: print("Bad File."); exit()

        ## Get OGR data layer
        ogrlayer = shapefile.GetLayer()

        ## Get data from ogrlayer, and return new VectorLayer
        fields, features = _data_from_OGR_layer(ogrlayer)

        new_lay = VectorLayer(None)
        new_lay._load_data(fields, features)
        return new_lay
    
    @staticmethod
    def from_geojson(path):
        ## Setup driver for shapefile, open shapefile
        driver = ogr.GetDriverByName('GeoJSON')
        datafile = driver.Open(path, 0)

        ## Test if file is readable
        if datafile == None: print("Bad File."); exit()

        ## Get OGR data layer
        ogrlayer = datafile.GetLayer()

        ## Get data from ogrlayer, and return new VectorLayer
        fields, features = _data_from_OGR_layer(ogrlayer)

        new_lay = VectorLayer(None)
        new_lay._load_data(fields, features)
        return new_lay



# TODO: Refactor these to be bit cleaner
def _get_geom_points(geom):
    """
    Given a OGR geometry, returns a list structure of points.
    """
    ## Create root point list
    feature_point_stuct = []

    if geom.GetGeometryName() in ("POINT", "MULTIPOINT"):
        ## Plain point
        if geom.GetGeometryCount() == 0:
            subgeom_struct = []

            for point in geom.GetPoints():
                subgeom_struct.append(point)

            feature_point_stuct.append(subgeom_struct)
        
        ## Muti Point
        else:
            for indx in range(geom.GetGeometryCount()):
                subpoly_geom = geom.GetGeometryRef(indx)
                subgeom_struct = []

                for point in subpoly_geom.GetPoints():
                    subgeom_struct.append(point)

                feature_point_stuct.append(subgeom_struct)

    

    elif geom.GetGeometryName() in ("LINESTRING", "MULTILINESTRING"):
        geocount = geom.GetGeometryCount()
        if geocount == 0:
            subgeom_struct = []

            for point in geom.GetPoints():
                subgeom_struct.append(point)

            feature_point_stuct.append(subgeom_struct)

        else:
            for indx in range(geom.GetGeometryCount()):
                subgeom = geom.GetGeometryRef(indx)
                subgeom_struct = []

                for point in subgeom.GetPoints():
                    subgeom_struct.append(point)

                feature_point_stuct.append(subgeom_struct)


    elif geom.GetGeometryName() in ("POLYGON", "LINEARRING", "MULTIPOLYGON"):
        for indx in range(geom.GetGeometryCount()):
            subpoly_geom = geom.GetGeometryRef(indx)
            subpoly_struct = []

            if subpoly_geom.GetGeometryName() == "POLYGON":
                subpoly_geom = subpoly_geom.GetGeometryRef(0)

            for point in subpoly_geom.GetPoints():
                subpoly_struct.append(point)

            feature_point_stuct.append(subpoly_struct)

    else:
        print("There is an unexpected geometry type.")
        print(geom.GetGeometryName())
        print()

    feature_points = []
    feature_struct = []

    for subfeat in feature_point_stuct:
        feature_struct.append(len(subfeat))
        for point in subfeat:
            feature_points.append(point)

    return feature_struct, np.array(feature_points)

def _data_from_OGR_layer(ogrlayer):
    """ REWRITE THIS FUNCTION """

    ## Create list of attributes field names from
    field_names = []
    attrib_data = ogrlayer.GetLayerDefn()
    field_count = attrib_data.GetFieldCount()
    for indx in range(field_count):
        field_data = attrib_data.GetFieldDefn(indx)
        field_names.append(field_data.GetName())


    features = list()

    ## Loop through all OGR features, creating _VectorFeatures
    for feature_ogr in ogrlayer:

        ## Extract attribute from ogr feature into feature_attributes list
        feature_attributes = []
        for indx in range(field_count):
            feature_attributes.append(feature_ogr.GetField(indx))

        feature_geom = feature_ogr.GetGeometryRef()
        feature_class = {"POINT": _PointFeature, 
                         "MULTIPOINT": _PointFeature,
                         "LINESTRING": _LineFeature, 
                         "MULTILINESTRING": _LineFeature, 
                         "POLYGON": _PolygonFeature,
                         "LINEARRING": _PolygonFeature,
                         "MULTIPOLYGON": _PolygonFeature}[feature_geom.GetGeometryName()]

        ## Create new VectorFeature to store
        new_feature = feature_class()
        new_feature._attributes = feature_attributes
        geoStruct, geo_points = _get_geom_points(feature_geom)

        new_feature._geom_struct = np.array(geoStruct)

        lon = [coord[1] for coord in geo_points]
        lat = [coord[0] for coord in geo_points]

        new_feature.import_geographic(lon, lat)

        features.append(new_feature)

    ## Return New vector Layer
    #return field_names, attributes_list, geometrys_list
    return field_names, features

'''
def from_shapefile(shapefile_path):
    """
    """
    ## Setup driver for shapefile, open shapefile
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shapefile = driver.Open(shapefile_path, 0)

    ## Test if file is readable
    if shapefile == None: print("Bad File."); exit()

    ## Get OGR data layer
    ogrlayer = shapefile.GetLayer()

    ## Get data from ogrlayer, and return new VectorLayer
    fields, geometry_type, features = _data_from_OGR_layer(ogrlayer)
    return VectorLayer(geometry_type, fields, features)
'''
