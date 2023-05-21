from typing import List, Union
from shapely.geometry import Point, LineString, MultiLineString
from shapely.ops import linemerge, nearest_points
from datetime import datetime
import random

class GPSSimulatorTools:
    
    buffer_value = 1e-8

    @classmethod
    def move_car(cls, lines: Union[LineString, MultiLineString], car: dict, old_time: datetime, new_time: datetime):
        """
        The main function responsible for the movement of the car (point).
        :param line: list of LineString or MultiLineString - roads
        :param car: dict
        :param old_time: datetime - the time at which the point was at a given location
        :param new_time: datetime - the time at which the new point is located
        """
        car_position = car['position']
        if car_position:
            for line in lines:
                if line.buffer(cls.buffer_value).intersects(car_position):
                    new_position = cls.move_along_line(car, line, old_time, new_time)
                    if new_position:
                        car['position'] = new_position
                    else:
                        nearest_line = cls.get_nearest_line(car_position, lines, line)
                        if nearest_line:
                            car["position"] = nearest_line.interpolate(nearest_line.project(car_position))
                        else:
                            car['speed'] = 0
                        car['direction'] = False if car['direction'] else True
                    break
    
    @classmethod
    def move_along_line(cls, car: dict, line: Union[LineString, MultiLineString], old_time: datetime, new_time: datetime) -> Union[Point, None]:
        """
        This function moves a point along a line in a specified direction, after a specified time and at a specified speed of movement
        :param car: dict
        :param line: LineString or MultiLineString - the current line
        :param old_time: datetime - the time at which the point was at a given location
        :param new_time: datetime - the time at which the new point is located
        :return: Point or None - new location of point. If the point is not on the line, the distance traveled exceeds the length of the line, or is less than zero, it returns None.
        """
        car_position = car['position']
        car_speed = car['speed']
        car_direction = car['direction']
        
        # Convert from km/h to m/s
        car_speed_mps = car_speed * 1000 / 3600
        time_diff = (new_time - old_time).total_seconds()
        
        distance = car_speed_mps * time_diff
        
        if isinstance(line, MultiLineString):
            line = linemerge(line)
        
        car_distance = line.project(car_position)
        
        if car_direction:
            distance_along_line = car_distance + distance
        else:
            distance_along_line = car_distance - distance
            
        new_location = line.interpolate(distance_along_line)
        
        if not line.buffer(cls.buffer_value).contains(new_location) or distance_along_line > line.length or distance_along_line < 0:
            return None
        
        distance_to_end = line.length - distance_along_line
        car['speed'] = cls.adjust_speed(car_speed, distance_to_end, line.length)
        return new_location
    
    @classmethod
    def get_nearest_line(cls, point: Point, lines: List[Union[LineString, MultiLineString]], 
                         current_line: Union[LineString, MultiLineString]) -> Union[LineString, MultiLineString]:
        """
        This function finds the line closest to the given point from a list of all lines, excluding the current line.
        :param point: Point - the current location
        :param lines: list of LineString or MultiLineString - the list of all lines
        :param current_line: LineString or MultiLineString - the current line
        :return: LineString - the line closest to the point
        """
        # Get the lines that are connected to the current line
        nearest_line = None
        min_distance = None
        connected_lines = cls.get_connected_lines(current_line, lines)

        # Exclude the current line
        connected_lines = [line for line in connected_lines if line != current_line]
        for line in connected_lines:
            point_on_line, point_on_point = nearest_points(line, point)
            distance = point_on_point.distance(point_on_line)

            if min_distance is None or distance < min_distance:
                min_distance = distance
                nearest_line = line

        return nearest_line
    
    @classmethod
    def adjust_speed(cls, current_speed: float, distance_to_line_end: float, road_length: float, 
                     max_acceleration: float = 10, max_deceleration: float = 10) -> float:
        """
        This function returns the speed of a vehicle based on its position on the road.
        :param current_speed: float- the current speed
        :param distance_to_line_end: float - Distance to the end of the line (road)
        :param road_length: float - Road length 
        :param max_acceleration: float - Maximum acceleration
        :param max_acceleration: float - Maximum deceleration
        :return: Float - vehicle speed value (movement of a point)
        """
        
        if distance_to_line_end < (road_length * 0.2):
            if current_speed > 10:
                speed_change = random.uniform(-max_deceleration, 0)
            else:
                speed_change = random.uniform(0, max_acceleration)
                
        else:
            speed_change = random.uniform(-max_deceleration, max_acceleration)

        new_speed = current_speed + speed_change

        return max(new_speed, 0)

    @staticmethod
    def get_connected_lines(current_line: Union[LineString, MultiLineString], all_lines: List[Union[LineString, MultiLineString]]) -> Union[LineString, MultiLineString]:
        """
        This function returns all lines that share an endpoint with the current line.
        :param current_line: LineString or MultiLineString - the current line
        :param all_lines: list of LineString or MultiLineString - the list of all lines
        :return: list of LineString or MultiLineString - the lines connected to the current line
        """
        connected_lines = []

        # Convert MultiLineString to individual LineStrings if necessary
        if isinstance(current_line, MultiLineString):
            current_lines = list(current_line.geoms)
        else:
            current_lines = [current_line]
        
        # Convert each MultiLineString in all_lines to individual LineStrings
        all_lines = [line for multiline in all_lines for line in (list(multiline.geoms) if isinstance(multiline, MultiLineString) else [multiline])]

        for current_line in current_lines:
            # Get the endpoints of the current line
            start_point = Point(current_line.coords[0])
            end_point = Point(current_line.coords[-1])

            for line in all_lines:
                if line == current_line:
                    continue  # Skip the current line

                # Check if the line shares an endpoint with the current line
                if (start_point.equals(Point(line.coords[0])) or
                    start_point.equals(Point(line.coords[-1])) or
                    end_point.equals(Point(line.coords[0])) or
                    end_point.equals(Point(line.coords[-1]))):
                    connected_lines.append(line)

        return connected_lines