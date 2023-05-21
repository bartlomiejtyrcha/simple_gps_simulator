import argparse
import json
import time
from datetime import datetime
from typing import List
from shapely.geometry import mapping
import os

from data.cars import Cars
from data.roads import GPSSimulatorRoads
from data.utils.simulator import GPSSimulatorTools

class SimpleGPSSimulator:
    
    def __init__(self, count_cars: int, source_geojson_file: str, result_filename: str, results: int = 10,
                 min_speed: float = 1, max_speed: float = 50):
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.source_geojson_file = source_geojson_file
        self.result_filename = result_filename
        
        self.cars = Cars(count_cars, min_speed, max_speed)
        self.roads = GPSSimulatorRoads(self.get_filename())
        self.results = results
        
        self.lines = self.roads.lines
        self.vehicles = self.cars.generate_car_list()
        self.cars.generate_cars_position(self.vehicles, self.roads.lines, self.roads.geojson.crs_info)
        
    def get_filename(self):
        file_path = os.path.join("roads_data", self.source_geojson_file)
        
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File '{file_path}' not found in the source folder.")
        
        absolute_path = os.path.abspath(file_path)
        return absolute_path

    def write_to_geojson(self, filename: str, features: list):
        check_filename = filename.split(".", 1)
        
        if len(check_filename) == 2 and check_filename[1] != 'geojson':
            return ValueError("The file should have the extension .geojson.")
        elif len(check_filename) == 1:
            check_filename = check_filename[0] + ".geojson"
            print("The .geojson extension will be added.")
            
        filename = check_filename.replace(" ", "")
        
        file_path = os.path.abspath(os.path.join("results", filename))
        
        with open(file_path, 'w') as f:
            json.dump(
                {
                    "type": "FeatureCollection",
                    "name": "exported",
                    "crs": { "type": "name", "properties": { "name": str(self.roads.geojson.crs_info) } },
                    "features": features
                }, 
            f)

    def generate(self):
        
        position_id = 0
        end = 0
        old_time = datetime.now()
        features = []
        while end < self.results:
            actual_time = datetime.now()
            for car in self.vehicles:
                GPSSimulatorTools.move_car(self.lines, car, old_time, actual_time)
            
                features.append({
                    "type": "Feature",
                    "geometry": mapping(car['position']),
                    "properties": {"id": position_id+1, "car_id": car['car_id'], "timestamp": actual_time.strftime("%d/%m/%Y, %H:%M:%S"), "speed": car['speed']}
                })
                position_id += 1
                
            old_time = actual_time
            time.sleep(1)
            end += 1
            
        self.write_to_geojson(self.result_filename, features)
    
    @staticmethod
    def get_source_files() -> List[str]:
        folder_path = "roads_data" 
        geojson_files = []

        for file_name in os.listdir(folder_path):
            if file_name.endswith(".geojson"):
                geojson_files.append(file_name)

        return geojson_files

def main():
    parser = argparse.ArgumentParser(description="Simple simulator of vehicles moving on roads")
    subparsers = parser.add_subparsers(dest='command')
    
    get_files_parser = subparsers.add_parser('get_source_files')
    
    generate_parser = subparsers.add_parser('generate')
    generate_parser.add_argument("count_cars", type=int, help="Number of cars to generate")
    generate_parser.add_argument("source_geojson_file", type=str, help="Name (with .geojson extension) of the source GeoJSON file")
    generate_parser.add_argument("result_filename", type=str, help="Name of the result file")
    generate_parser.add_argument("-results", type=int, default=10, help="Number of simulation results (default: 10)")
    generate_parser.add_argument("-min_speed", type=float, default=1, help="Minimum speed of vehicles (default: 1)")
    generate_parser.add_argument("-max_speed", type=float, default=50, help="Maximum speed of vehicles (default: 50)")
    
    parser.add_argument("generate", action="store_true", help="Generate simulation results")
    parser.add_argument("get_source_files", action="store_true", help="Get source files")
    
    args = parser.parse_args()
    
    if args.command == 'generate':
        simulator = SimpleGPSSimulator(
            count_cars=args.count_cars, 
            source_geojson_file=args.source_geojson_file, 
            result_filename=args.result_filename, 
            results=args.results, 
            min_speed=args.min_speed, 
            max_speed=args.max_speed
        )
        simulator.generate()

    if args.command == 'get_source_files':
        print(SimpleGPSSimulator.get_source_files())
    
if __name__ == "__main__":
    main()
