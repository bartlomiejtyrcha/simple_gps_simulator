from shapely.geometry import shape

from data.utils.reader import GeoJSONReader

class GPSSimulatorRoads:
    def __init__(self, geojson_path: str):
        self.geojson = GeoJSONReader(geojson_path)
        self.lines = [shape(feature['geometry']) for feature in self.geojson.features]