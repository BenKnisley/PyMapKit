#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date: December 31, 2019
"""

## Import OGR
from osgeo import ogr
import multiprocessing

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

    if geom.GetGeometryName() == "POINT":
        for point in geom.GetPoints():
            feature_point_stuct = point

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
        print("There is an unexpected geometry type. WTF")
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

def from_shapefile(MapEngine_obj, shapefile_path):
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
    return VectorLayer(MapEngine_obj, geometry_type, geometrys_list, field_names, attributes_list)


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
    colors = [(1,0,0),
              (0,1,0),
              (0,0,1),
              (0,0.5,0),
              (0.5,0.5,0.5),
              (0.5,0,0)]

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
        self.polyLineColor = (0.0, 1.0, 0.5)
        self.polyLineWidth = 0.5


class VectorLayer:
    """ """
    def __init__(self, host_map_engine, geotype, geom_data, field_names, attributes_list):
        """ """
        ##
        #! MAKE THESE PRIVATE
        self._map_engine = host_map_engine
        self.geotype = geotype
        self.rawdata = geom_data #! RENAME THIS
        self.fields = field_names
        self.attributes_store = attributes_list


        self.features = []
        self.attributes = []
        self.styles = []

        self.projectData()

        ## Set Defalt map style to each feature
        for _ in self.features:
            new_style = _FeatureStyle()
            self.styles.append(new_style)

    def setStyle(self, index, style):
        """ """
        None

    def projectData(self):
        """ """
        ## Clear existing features
        self.features = []

        ## If source and destination proj are same, skip projection overhead
        if self._map_engine._WGS84 == self._map_engine._proj:
            self.features = self.rawdata
            return

        if self.geotype == 'point':
            ## No multiprocessing, already optimized
            self.features = self._project_points(self.rawdata)

        elif self.geotype == 'line':
            with multiprocessing.Pool(processes=8) as pool:
                self.features = pool.map(self._project_line, self.rawdata)

        elif self.geotype == 'polygon':
            with multiprocessing.Pool(processes=8) as pool:
                self.features = pool.map(self._project_poly, self.rawdata)

    def _project_points(self, geofeatures):
        """ projectData Helper function """
        return self._map_engine.geo2proj(geofeatures)

    def _project_line(self, geoline):
        """ projectData Helper function """
        projline = []
        for subline in geoline:
            projline.append( self._map_engine.geo2proj(subline) )
        return projline

    def _project_poly(self, geopoly):
        """ projectData Helper function """
        projpoly = []
        for subpoly in geopoly:
            projpoly.append( self._map_engine.geo2proj(subpoly) )
        return projpoly




    def draw(self, cr):
        if self.geotype == 'point':
            pixPoints = self._map_engine.proj2pix(self.features)
            for point, style in zip(pixPoints, self.styles):
                self._map_engine._map_painter.drawPoint(cr, point, style)

        elif self.geotype == 'line':
            for projLine, style in zip(self.features, self.styles):
                pixLine = []
                for subline in projLine:
                    pix_subline = self._map_engine.proj2pix(subline)
                    pixLine.append(pix_subline)
                self._map_engine._map_painter.drawLine(cr, pixLine, style)

        else: # self.geotype == polygon:
            for projFeature, style in zip(self.features, self.styles):
                pixPoly = []
                for subPoly in projFeature:
                    pixsubPoly = self._map_engine.proj2pix(subPoly)
                    pixPoly.append(pixsubPoly)

                self._map_engine._map_painter.drawPolygon(cr, pixPoly, style)
