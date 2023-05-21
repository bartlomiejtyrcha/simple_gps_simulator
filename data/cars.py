import random
from shapely.geometry import shape, LineString, MultiLineString
from pyproj import CRS, Transformer

class Cars:
    def __init__(self, count_cars: int, min_speed: float, max_speed: float):
        self.count_cars = count_cars
        self.min_speed = min_speed
        self.max_speed = max_speed
    
    def generate_car_list(self) -> list:
        car_list = []
        car_names = ['Toyota', 'Honda', 'Ford', 'Chevrolet', 'BMW', 'Mercedes', 'Audi', 'Volkswagen', 'Tesla']

        for car_id in range(self.count_cars):
            car_name = random.choice(car_names)
            car_info = {'car_id': car_id+1,'name': car_name, 'speed': self.get_car_speed()}
            car_list.append(car_info)

        return car_list
    
    def get_car_speed(self):
        return round(random.uniform(self.min_speed, self.max_speed), 2)

    def generate_cars_position(self, cars: list, lines: list, crs_info):
        
        for car in cars:
            line = random.choice(lines)
            car["position"] = self.get_random_point_on_line(line, crs_info)
            car["direction"] = random.choice([True, False])
        
    def get_random_point_on_line(self, line, crs_info):
        line_length_m = self.line_length(line, crs_info)
        random_fraction = random.uniform(0, line_length_m)
        random_point_on_line = line.interpolate(random_fraction)
        
        return random_point_on_line

    def line_length(self, line, crs_info):
        source_crs = crs_info
        target_crs = CRS.from_epsg(3857)
        transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)
        total_length_in_meters = 0

        if isinstance(line, LineString):
            transformed_linestring = transformer.transform(line.xy[0], line.xy[1])
            length_in_meters = LineString(list(zip(*transformed_linestring))).length
            total_length_in_meters += length_in_meters
        elif isinstance(line, MultiLineString):
            for linestring in line.geoms:
                transformed_linestring = transformer.transform(linestring.xy[0], linestring.xy[1])
                length_in_meters = LineString(list(zip(*transformed_linestring))).length
                total_length_in_meters += length_in_meters

        return total_length_in_meters