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


def style_by_attribute(input_layer, **kw):
    """ This is a junk function, not to be kept. """

    newstyle = _FeatureStyle()
    newstyle.polyColor = (1,0,1)

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
