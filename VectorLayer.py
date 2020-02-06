#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date: December 31, 2019
"""

## Import OGR
from osgeo import ogr
import multiprocessing
import numpy as np

def _get_geom_points(geom):
    """
    Given a OGR geometry, returns a list structure of points.

    Maybe use recurcion

    WKBGeometryTypes
    wkbPoint = 1,
    wkbLineString = 2,
    wkbPolygon = 3,
    wkbMultiPoint = 4,
    wkbMultiLineString = 5,
    wkbMultiPolygon = 6,
    wkbGeometryCollection = 7
    """
    ## Create root point list
    feature_point_stuct = []

    if geom.GetGeometryName() in ("POINT", "MULTIPOINT"):
        subgeom_struct = []
        for point in geom.GetPoints():
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

    ## Return root point list
    return feature_point_stuct

def _data_from_OGR_layer(ogrlayer):

    ## Set int GetGeomType to string of geom type
    geometry_type = [None, 'point', 'line', 'polygon'][ogrlayer.GetGeomType()]

    ## Get layer field metadata
    attrib_data = ogrlayer.GetLayerDefn()

    ## Create list of attributes field names
    field_names = []
    field_count = attrib_data.GetFieldCount()
    for indx in range(field_count):
        field_data = attrib_data.GetFieldDefn(indx)
        field_names.append(field_data.GetName())

    ## Create lists to hold lists of attributes and geometrys
    attributes_list = []
    geometrys_list = []

    ## Loop through all features, loading attributes & geometry lists
    for feature in ogrlayer:
        feature_attributes = []
        for indx in range(field_count):
            feature_attributes.append(feature.GetField(indx))
        attributes_list.append(feature_attributes)
        geometrys_list.append(_get_geom_points(feature.GetGeometryRef()))

    ## Return New vector Layer
    return field_names, attributes_list, geometry_type, geometrys_list

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
    field_names, attributes_list, geometry_type, geometrys_list = _data_from_OGR_layer(ogrlayer)
    return VectorLayer(geometry_type, geometrys_list, field_names, attributes_list)

def color_parse(input_color):
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

def style_by_attribute(input_layer, color, **kw):
    """ This is a junk function, not to be kept. """

    newstyle = _FeatureStyle()
    newstyle.polyColor = color_parse(color)

    for field in kw:
        input_value = kw[field]
        if field not in input_layer.fields: print("Bad attribute name"); return

        field_index = input_layer.fields.index(field)

        for indx, featureAttrb in enumerate(input_layer.attributes_store):
            if featureAttrb[field_index] == input_value:
                input_layer.styles[indx] = newstyle

def style_layer_random(input_layer):
    """ This is a junk function, not to be kept. """
    ## Define colors in list
    #colors = [(0.768,0.47,0.53), (0,1,0), (0,0,1), (0,0.5,0), (0.5,0.5,0.5), (0.5,0,0)]
    #colors = [(color[0]*255, color[1]*255, color[2]*255) for color in colors]

    colors = [
        (228,26,28),
        (55,126,184),
        (77,175,74),
        (152,78,163),
        (255,127,0)
    ]
    colors = [(color[0]/255.0, color[1]/255.0, color[2]/255.0) for color in colors]


    counter = 0
    for style in input_layer.styles:
        style.polyColor = colors[counter]

        counter += 1
        if counter == len(colors): counter = 0


class _FeatureStyle:
    """ """
    def __init__(self):
        self.pointcolor = (0.61, 0.13, 0.15)
        self.pointradius = 2

        self.linecolor = (0,0,1)
        self.linewidth = 1

        self.polyColor = (0.31, 0.34, 0.68)
        self.polyLineColor = (0.0, 0.0, 0.0)
        self.polyLineWidth = 0.5


class VectorLayer:
    """ """
    def __init__(self, geotype, geom_data, field_names, attributes_list):
        """ """
        ##
        #! MAKE THESE PRIVATE
        self._MapEngine = None ## Set as none when not added to MapEngine
        self.geotype = geotype
        self.rawdata = geom_data #! RENAME THIS
        self.fields = field_names
        self.attributes_store = attributes_list

        self.features = []
        self.attributes = []
        self.styles = []

        ## Set Defalt map style to each feature
        for _ in self.rawdata:
            new_style = _FeatureStyle()
            self.styles.append(new_style)

    def _activate(self, new_MapEngine):
        """ Function called when layer is added to a MapEngine """
        self._MapEngine = new_MapEngine
        self.projectData()

    def _deactivate(self):
        """ Function called when layer is added to a MapEngine """
        self._MapEngine = None
        self.features.clear()

    def setStyle(self, index, style):
        """ """
        None


    def projectData(self):
        ## Clear existing features
        self.features = []

        ## If source and destination proj are same, skip projection overhead
        if self._MapEngine._WGS84 == self._MapEngine._projection:
            self.features = self.rawdata
            return

        ## Break features into structure and points
        structure = []
        point_list = []

        ## Loop each raw feature, building structure, & list of points
        for feature in self.rawdata:
            feature_structure = []
            for subfeatures in feature:
                feature_structure.append(len(subfeatures))
                for point in subfeatures:
                    point_list.append(point)
            structure.append(feature_structure)

        ## Project all points in bulk
        proj_points = self._MapEngine.geo2proj(point_list)

        ## Rebuild features from points and structure
        point_pointer = 0
        for feature in structure:
            proj_feature = []
            for sub_pnt_cnt in feature:
                proj_feature.append(proj_points[point_pointer:point_pointer+sub_pnt_cnt])
                point_pointer += sub_pnt_cnt
            self.features.append(proj_feature)


    def draw(self, cr):
        if self.geotype == 'point':
            for projPoint, style in zip(self.features, self.styles):
                pixPoint = []
                for subPoint in projPoint:
                    pixPoint.append(self._MapEngine.proj2pix(subPoint))
                self._MapEngine._map_painter.drawPoint(cr, pixPoint, style)

        elif self.geotype == 'line':
            for projLine, style in zip(self.features, self.styles):
                pixLine = []
                for subline in projLine:
                    pix_subline = self._MapEngine.proj2pix(subline)
                    pixLine.append(pix_subline)
                self._MapEngine._map_painter.drawLine(cr, pixLine, style)

        else: # self.geotype == polygon:
            for projFeature, style in zip(self.features, self.styles):
                pixPoly = []
                for subPoly in projFeature:
                    pixsubPoly = self._MapEngine.proj2pix(subPoly)
                    pixPoly.append(pixsubPoly)

                self._MapEngine._map_painter.drawPolygon(cr, pixPoly, style)
