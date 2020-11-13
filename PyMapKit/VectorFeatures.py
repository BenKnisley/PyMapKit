"""
Author: Ben Knisley [benknisley@gmail.com]
Date: 24 Oct, 2020
"""
import pyproj


class Geometry:
    """ """
    def __init__(self, parent, geometry_type):
        self.parent = parent
        self.geometry_type = geometry_type
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
                    if(math.isclose(test_x, point_x, abs_tol=self.parent.parent._proj_scale*5) and
                        math.isclose(test_y, point_y, abs_tol=self.parent.parent._proj_scale*5)):
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
                            pix_dist = dist / self.parent.parent._proj_scale

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
    """ """
    def __init__(self, attributes_names, geometry):
        self.attributes = {}
        for field in attributes_names:
            self.attributes[field] = None
        
        self.geometry = geometry
    
    def __getitem__(self, field_name):
        return self.attributes[field_name]

    def __setitem__(self, field_name, value):
        self.attributes[field_name] = value

class FeatureHost:
    """ """
    def __init__(self, geometry_type, field_names, projection="EPSG:4326"):
        self.field_names = field_names
        self.features = []

        self.projection = pyproj.Proj(projection)
        self.geometry_type = geometry_type
        self.geometries = []
        self.x_values = []
        self.y_values = []
    
    def __getitem__(self, key):
        if isinstance(key, int):
            return self.features[key]
        else: 
            return FeatureDict(self, key)
    
    def __len__(self):
        return len(self.features)

    def __repr__(self):
        repr_string = f"{self.geometry_type.capitalize()} feature set with {len(self)} features."
        return repr_string
    
    def __add__(self, other):
        new_set = FeatureSet(self.geometry_type, self.field_names, self.projection.srs)
        
        for feature in self:
            new_set.add(feature)
        
        for feature in other:
            new_set.add(feature)

        return new_set

    def new(self):
        """
        Creates a new feature inside FeatureSet
        """
        #! ADD A PROJECTION CHECK & FIELDS CHECK

        new_geom = Geometry(self, self.geometry_type)
        self.geometries.append(new_geom)

        new_feature = Feature(self.field_names, new_geom)
        self.features.append(new_feature)

        return new_feature

    def add(self, old_feature):
        """
        Adds an existing feature inside FeatureSet
        """
        new_geom = Geometry(self, self.geometry_type)
        self.geometries.append(new_geom)

        new_feature = Feature(self.field_names, new_geom)
        self.features.append(new_feature)

        new_geom.structure = old_feature.geometry.structure.copy()

        x_values, y_values = old_feature.geometry.get_points()
        self.x_values += x_values
        self.y_values += y_values

        for field_name in self.field_names:
            new_feature[field_name] = old_feature[field_name]

        return new_feature

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

class FeatureList:
    """ """
    def __init__(self, parent, features):
        self.parent = parent
        self.features = features
    
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
    
    def to_feature_set(self):
        new_vector_host = FeatureSet(self.parent.geometry_type, self.parent.field_names, self.parent.projection.srs)
        for f in self:
            new_vector_host.add(f)
        return new_vector_host

    def run_on_all(self, method_name, *args):
        has_return = False
        rtrn_list = []
        for rtrn in map(methodcaller(method_name, *args), self.features):
            has_return = has_return or bool(rtrn)
            rtrn_list.append(rtrn)

class FeatureDict:
    """ """
    def __init__(self, parent, field):
        self.parent = parent
        self.field = field
        self.keys = []
        self.features = []

        self.output_class = FeatureList

        for feature in self.parent.features:
            self.features.append(feature)
            self.keys.append(feature[self.field])
    
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
