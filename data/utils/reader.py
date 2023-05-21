import json
from pyproj import CRS

class GeoJSONReader:
    def __init__(self, filename):
        self.filename = filename
        self.load()
        self.object_count = self.get_object_count()
        self.features = self.data.get("features")
    
    def load(self):
        with open(self.filename) as f:
            self.data = json.load(f)
            self.get_crs_info()
    
    def get_crs_info(self):
        crs = self.data.get('crs')
        if crs:
            crs_properties = crs.get('properties')
            if crs_properties:
                crs_epsg = crs_properties.get('name')
                if crs_epsg:
                    self.crs_info = CRS.from_string(crs_epsg)
    
    def get_object_count(self):
        features = self.data.get('features')
        result = None
        if features:
            result = len(features)
        return result
