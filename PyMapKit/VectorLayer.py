#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date: Febuary 8, 2020

Notes:

Add a VectorLayer.run method that takes a function to style
features.

Remove _color_converter function, and add color cache for each color


Remove numpy arrays and use python lists instead in some places
"""
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
        self._color = (0.61, 0.13, 0.15)
        self._radius = 2

    #! TODO: Add a set icon function, to draw image instead of plain circle

    def set_color(self, input):
        """ """
        self._color = _color_converter(input)

    def set_size(self, input):
        self._radius = input / 2

    def draw(self, layer, renderer, cr):
        ## Calulate pixel values
        pix_x, pix_y = layer._MapEngine.proj2pix(self._proj_x, self._proj_y)

        ## Draw point
        renderer.draw_point(cr, self._geom_struct, pix_x, pix_y, self._color, self._radius, layer._alpha)
        
class _LineFeature(_VectorFeature):
    """ """
    def __init__(self):
        """ """
        self._color = (0.31, 0.34, 0.68)
        self._width = 1

    def set_color(self, input_color):
        """ """
        self._color = _color_converter(input_color)

    def set_size(self, input_width):
        """ """
        self._width = input_width

    def draw(self, layer, renderer, cr):
        ## Calulate pixel values
        pix_x, pix_y = layer._MapEngine.proj2pix(self._proj_x, self._proj_y)
        renderer.draw_line(cr, self._geom_struct, pix_x, pix_y, self._width, self._color, layer._alpha)

class _PolygonFeature(_VectorFeature):
    """ """
    def __init__(self):
        """ """
        self._bgcolor = (0.31, 0.34, 0.68)
        self._line_color = (1.0, 1.0, 1.0)
        self._line_width = 1

    def set_color(self, input_color):
        """ """
        self._bgcolor = _color_converter(input_color)

    def set_line_color(self, input_color):
        """ """
        self._line_color = _color_converter(input_color)

    def set_line_width(self, input_width):
        """ """
        self._line_width = input_width

    def draw(self, layer, renderer, cr):
        """ """
        ## Calulate pixel values
        #""" ## Full layer vectorization proj2pix optimization
        pix_x, pix_y = self._pix_x, self. _pix_y
        """ ## Single Vector iteration proj2pix
        pix_x, pix_y = layer._MapEngine.proj2pix(self._proj_x, self._proj_y)
        #"""

        ## Call on renderer to render polygon
        renderer.draw_polygon(cr, self._geom_struct, pix_x, pix_y, self._bgcolor, self._line_width, self._line_color, layer._alpha)


class VectorLayer:
    """ """
    def __init__(self, path=None):
        """ """
        self._MapEngine = None
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
        """ """
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

    def _activate(self, new_MapEngine):
        """ Function called when layer is added to a MapEngine layer list."""
        self._MapEngine = new_MapEngine
        self._project_features()

    def _deactivate(self):
        """ Function called when layer is added to a MapEngine """
        pass
        
    def focus(self):
        """ """
        self._MapEngine._projx, self._MapEngine._projy = self._focus_point
        s_x = (self._extent[1] - self._extent[0]) / self._MapEngine.width
        s_y = (self._extent[3] - self._extent[2]) / self._MapEngine.height
        self._MapEngine.set_scale( max(s_x, s_y) )

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
        grand_proj_point_x_list, grand_proj_point_y_list = self._MapEngine.geo2proj(grand_geo_point_y_list, grand_geo_point_x_list)

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

        self._pix_x_cache, self._pix_y_cache = self._MapEngine.proj2pix(self._proj_x_cache, self._proj_y_cache)

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

def _color_converter(input_color):
    """ Converts different color formats into single format.

    Inputs:
        - (float, float, float) - A tuple of three floats between 0.0 and 1.0
            representing red, green, & blue values respectively.

        - (int, int, int) - A tuple of three ints between 0 and 1
            representing red, green, & blue values respectively.

        - "#0F0F0F" - A html color hex string.

        - "colorname" - A html color name.

    Returns:
        - (float, float, float) - A tuple of three floats between 0.0 and 1.0
            representing red, green, & blue values respectively.

    """
    ## Two tuple types, 0-1 or 0-256
    if isinstance(input_color, tuple):

        ## If float tuple, input same as output
        if isinstance(input_color[0], float):
            return input_color

        if isinstance(input_color[0], int):
            R = input_color[3] / 255.0
            G = input_color[5] / 255.0
            B = input_color[7] / 255.0
            return (R,G,B)

    ## Two types of color strings: Html color names and hex
    if isinstance(input_color, str):
        ## Define color dictionary, with html color names defined
        color_dict = {"aliceblue": "#f0f8ff", "antiquewhite": "#faebd7", "aqua": "#00ffff", "aquamarine": "#7fffd4", "azure": "#f0ffff", "beige": "#f5f5dc", "bisque": "#ffe4c4", "black": "#000000", "blanchedalmond": "#ffebcd", "blue": "#0000ff", "blueviolet": "#8a2be2", "brown": "#a52a2a", "burlywood": "#deb887", "cadetblue": "#5f9ea0", "chartreuse": "#7fff00", "chocolate": "#d2691e", "coral": "#ff7f50", "cornflowerblue": "#6495ed", "cornsilk": "#fff8dc", "crimson": "#dc143c", "cyan": "#00ffff", "darkblue": "#00008b", "darkcyan": "#008b8b", "darkgoldenrod": "#b8860b", "darkgray": "#a9a9a9", "darkgreen": "#006400", "darkkhaki": "#bdb76b", "darkmagenta": "#8b008b", "darkolivegreen": "#556b2f", "darkorange": "#ff8c00", "darkorchid": "#9932cc", "darkred": "#8b0000", "darksalmon": "#e9967a", "darkseagreen": "#8fbc8f", "darkslateblue": "#483d8b", "darkslategray": "#2f4f4f", "darkturquoise": "#00ced1", "darkviolet": "#9400d3", "deeppink": "#ff1493", "deepskyblue": "#00bfff", "dimgray": "#696969", "dodgerblue": "#1e90ff", "firebrick": "#b22222", "floralwhite": "#fffaf0", "forestgreen": "#228b22", "fuchsia": "#ff00ff", "gainsboro": "#dcdcdc", "ghostwhite": "#f8f8ff", "gold": "#ffd700", "goldenrod": "#daa520", "gray": "#808080", "green": "#008000", "greenyellow": "#adff2f", "honeydew": "#f0fff0", "hotpink": "#ff69b4", "indianred": "#cd5c5c", "indigo": "#4b0082", "ivory": "#fffff0", "khaki": "#f0e68c", "lavender": "#e6e6fa", "lavenderblush": "#fff0f5", "lawngreen": "#7cfc00", "lemonchiffon": "#fffacd", "lightblue": "#add8e6", "lightcoral": "#f08080", "lightcyan": "#e0ffff", "lightgoldenrodyellow": "#fafad2", "lightgray": "#d3d3d3", "lightgreen": "#90ee90", "lightpink": "#ffb6c1", "lightsalmon": "#ffa07a", "lightseagreen": "#20b2aa", "lightskyblue": "#87cefa", "lightslategray": "#778899", "lightsteelblue": "#b0c4de", "lightyellow": "#ffffe0", "lime": "#00ff00", "limegreen": "#32cd32", "linen": "#faf0e6", "magenta": "#ff00ff", "maroon": "#800000", "mediumaquamarine": "#66cdaa", "mediumblue": "#0000cd", "mediumorchid": "#ba55d3", "mediumpurple": "#9370d8", "mediumseagreen": "#3cb371", "mediumslateblue": "#7b68ee", "mediumspringgreen": "#00fa9a", "mediumturquoise": "#48d1cc", "mediumvioletred": "#c71585", "midnightblue": "#191970", "mintcream": "#f5fffa", "mistyrose": "#ffe4e1", "moccasin": "#ffe4b5", "navajowhite": "#ffdead", "navy": "#000080", "oldlace": "#fdf5e6", "olive": "#808000", "olivedrab": "#6b8e23", "orange": "#ffa500", "orangered": "#ff4500", "orchid": "#da70d6", "palegoldenrod": "#eee8aa", "palegreen": "#98fb98", "paleturquoise": "#afeeee", "palevioletred": "#db7093", "papayawhip": "#ffefd5", "peachpuff": "#ffdab9", "peru": "#cd853f", "pink": "#ffc0cb", "plum": "#dda0dd", "powderblue": "#b0e0e6", "purple": "#800080", "red": "#ff0000", "rosybrown": "#bc8f8f", "royalblue": "#4169e1", "saddlebrown": "#8b4513", "salmon": "#fa8072", "sandybrown": "#f4a460", "seagreen": "#2e8b57", "seashell": "#fff5ee", "sienna": "#a0522d", "silver": "#c0c0c0", "skyblue": "#87ceeb", "slateblue": "#6a5acd", "slategray": "#708090", "snow": "#fffafa", "springgreen": "#00ff7f", "steelblue": "#4682b4", "tan": "#d2b48c", "teal": "#008080", "thistle": "#d8bfd8", "tomato": "#ff6347", "turquoise": "#40e0d0", "violet": "#ee82ee", "wheat": "#f5deb3", "white": "#ffffff", "whitesmoke": "#f5f5f5", "yellow": "#ffff00", "yellowgreen": "#9acd32"}

        if input_color.lower() in color_dict:
            input_color = color_dict[input_color.lower()]


        if '#' in input_color and len(input_color) == 7:
            ## Hex string color
            R = int(input_color[1:3], 16) / 255.0
            G = int(input_color[3:5], 16) / 255.0
            B = int(input_color[5:7], 16) / 255.0
            return (R,G,B)
