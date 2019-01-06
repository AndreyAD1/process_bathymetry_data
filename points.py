from itertools import tee
from math import hypot, inf

from datetime import datetime
import utm


class Point:
    def __init__(
            self,
            latitude: float,
            longitude: float,
            input_filepath: str =None
    ):
        self.latitude = latitude
        self.longitude = longitude
        self.input_filepath = input_filepath

    def convert_geocoordinates_to_utm(self):
        utm_long, utm_lat, zone_num, zone_letter = utm.from_latlon(
            self.latitude, self.longitude
        )
        self.latitude = utm_lat
        self.longitude = utm_long


class BathymetryPoint(Point):
    def __init__(
            self,
            latitude: float,
            longitude: float,
            measurement_datetime: datetime,
            depth: float,
            input_filepath: str = None,
            distance_from_sea: float = None,
            water_elevation: float = None,
            bottom_elevation: float = None,
            upper_log_name: str = None,
            lower_log_name: str = None
    ):
        super().__init__(latitude, longitude, input_filepath)
        self.measurement_datetime = measurement_datetime
        self.depth = depth
        self.distance_from_sea = distance_from_sea
        self.water_elevation = water_elevation
        self.bottom_elevation = bottom_elevation
        self.upper_logger_name = upper_log_name
        self.lower_logger_name = lower_log_name

    @staticmethod
    def get_distance_to_the_fairway_point(fairway_point: dict, lat, long):
        fairway_point_lat = fairway_point['latitude']
        fairway_point_long = fairway_point['longitude']
        only_numbers = fairway_point_lat and fairway_point_long and lat and long
        if only_numbers:
            distance = hypot(fairway_point_lat - lat, fairway_point_long - long)
            return distance
        return inf

    def get_distance_from_sea(self, points_along_fairway: dict):
        closest_fairway_point = min(
            points_along_fairway,
            key=lambda x: self.get_distance_to_the_fairway_point(
                x,
                self.latitude,
                self.longitude
            )
        )
        self.distance_from_sea = float(
            closest_fairway_point['distance_from_seashore']
        )

    def get_loggers_working_at_measurement_time(
            self,
            list_of_logger_points,
            logger_data,
    ):
        not_working_logger_names = []
        list_of_working_loggers = []
        for logger_name in logger_data:
            if self.measurement_datetime not in logger_data[logger_name]:
                not_working_logger_names.append(logger_name)
        for logger_point in list_of_logger_points:
            if logger_point['logger_name'] not in not_working_logger_names:
                list_of_working_loggers.append(logger_point)
        return list_of_working_loggers, not_working_logger_names

    def get_nearest_loggers(self, logger_list):
        logger_list.sort(key=lambda x: x['distance_from_seashore'])
        logger_iterator, logger_iterator_duplicate = tee(logger_list)
        next(logger_iterator_duplicate)
        pairwise_logger_list = zip(logger_iterator, logger_iterator_duplicate)

        for lower_logger, upper_logger in pairwise_logger_list:
            low_log_distance = lower_logger['distance_from_seashore']
            up_log_distance = upper_logger['distance_from_seashore']
            if self.distance_from_sea < low_log_distance:
                return lower_logger, upper_logger
            if low_log_distance <= self.distance_from_sea < up_log_distance:
                return lower_logger, upper_logger

        uppermost_loggers = (lower_logger, upper_logger)
        return uppermost_loggers

    def interpolate_water_surface(
            self,
            lower_level,
            upper_level,
            lower_distance,
            upper_distance,
    ):
        water_slope = (lower_level - upper_level) / (lower_distance - upper_distance)
        y_intercept = upper_level - water_slope * upper_distance
        water_elevation = water_slope * self.distance_from_sea + y_intercept
        return water_elevation

    def get_water_elevation(self, logger_data_points, logger_traces):
        working_logs, disabled_logs = self.get_loggers_working_at_measurement_time(
            logger_data_points,
            logger_traces,
        )
        lower_log, upper_log = self.get_nearest_loggers(
            working_logs
        )
        lower_log_name = lower_log['logger_name']
        upper_log_name = upper_log['logger_name']
        lower_elevation = logger_traces[lower_log_name][self.measurement_datetime]
        upper_elevation = logger_traces[upper_log_name][self.measurement_datetime]
        self.water_elevation = self.interpolate_water_surface(
            lower_elevation,
            upper_elevation,
            lower_log['distance_from_seashore'],
            upper_log['distance_from_seashore'],
        )
        self.upper_logger_name = upper_log_name
        self.lower_logger_name = lower_log_name
        return disabled_logs

    def get_bottom_elevation(self):
        self.bottom_elevation = self.water_elevation - self.depth


class LoggerPoint(Point):
    def __init__(
            self,
            logger_name,
            latitude,
            longitude,
            input_filepath=None,
            distance_from_sea=None,
            logger_data=None,
            switched_on=True
    ):
        super().__init__(latitude, longitude, input_filepath)
        self.name = logger_name
        self.distance_from_sea = distance_from_sea
        self.logger_data = logger_data
        self.switched_on = switched_on

    def get_logger_data(self):
        self.logger_data = []

    def check_switched_on_status(self):
        pass


class FairwayPoint(Point):
    def __init__(
            self,
            latitude,
            longitude,
            distance_from_sea,
            input_filepath=None
    ):
        super().__init__(latitude, longitude, input_filepath)
        self.distance_from_sea = distance_from_sea
