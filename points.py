from collections import OrderedDict
from datetime import datetime, timedelta
from itertools import tee
from math import hypot
from typing import Dict

import utm


class Point:
    def __init__(
            self,
            latitude: float,
            longitude: float,
            input_filepath: str = None
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


class FairwayPoint(Point):
    def __init__(
            self,
            latitude: float,
            longitude: float,
            distance_from_sea: float,
            input_filepath: str = ''
    ):
        super().__init__(latitude, longitude, input_filepath)
        self.distance_from_sea = distance_from_sea
        self.input_filepath = input_filepath


class LoggerPoint(Point):
    def __init__(
            self,
            logger_name: str,
            latitude: float,
            longitude: float,
            input_filepath: str = '',
            distance_from_sea: float = None,
            logger_data: Dict = None,
    ):
        super().__init__(latitude, longitude, input_filepath)
        self.logger_name = logger_name
        self.distance_from_sea = distance_from_sea
        self.logger_data = OrderedDict(
            sorted(logger_data.items(), key=lambda t: t[0])
        )

    def get_distance_from_sea(self, points_along_fairway: list):
        closest_fairway_point = min(
            points_along_fairway,
            key=lambda x: hypot(
                x.latitude - self.latitude,
                x.longitude - self.longitude
            )
        )
        self.distance_from_sea = closest_fairway_point.distance_from_sea

    def round_logger_datetime(self):
        rounded_logger_data = {}
        for measurement_datetime, water_elevation in self.logger_data.items():
            measurement_datetime += timedelta(seconds=30)
            rounded_datetime = measurement_datetime - timedelta(
                seconds=measurement_datetime.second,
                microseconds=measurement_datetime.microsecond
            )
            rounded_logger_data[rounded_datetime] = water_elevation
        self.logger_data = rounded_logger_data


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
            upper_logger: LoggerPoint = None,
            lower_logger: LoggerPoint = None,
    ):
        super().__init__(latitude, longitude, input_filepath)
        self.measurement_datetime = measurement_datetime
        self.depth = depth
        self.distance_from_sea = distance_from_sea
        self.water_elevation = water_elevation
        self.bottom_elevation = bottom_elevation
        self.upper_logger = upper_logger
        self.lower_logger = lower_logger
        self.switched_on_loggers = []
        self.switched_off_loggers = []

    def get_distance_from_sea(self, points_along_fairway: list):
        closest_fairway_point = min(
            points_along_fairway,
            key=lambda x: hypot(
                x.latitude - self.latitude,
                x.longitude - self.longitude
            )
        )
        self.distance_from_sea = closest_fairway_point.distance_from_sea

    def get_closest_logger_times(self, logger: LoggerPoint) -> tuple:
        logger_datetimes = list(logger.logger_data.keys())
        previous_logger_time = None
        for logger_time in logger_datetimes:
            if self.measurement_datetime < logger_time:
                return previous_logger_time, logger_time
            previous_logger_time = logger_time
        return previous_logger_time, None

    def get_loggers_working_at_measurement_time(
            self,
            loggers,
    ):
        switch_off_threshold = timedelta(minutes=15)
        for logger in loggers:
            closest_logger_times = self.get_closest_logger_times(logger)
            if None in closest_logger_times:
                self.switched_off_loggers.append(logger)
                continue
            time_difference = closest_logger_times[1] - closest_logger_times[0]
            if time_difference < switch_off_threshold:
                self.switched_on_loggers.append(logger)
            else:
                self.switched_off_loggers.append(logger)

    def get_nearest_loggers(self):
        self.switched_on_loggers.sort(key=lambda x: x.distance_from_sea)
        logger_iterator, logger_iterator_duplicate = tee(
            self.switched_on_loggers
        )
        next(logger_iterator_duplicate)
        pairwise_logger_list = zip(logger_iterator, logger_iterator_duplicate)

        for lower_logger, upper_logger in pairwise_logger_list:
            low_log_distance = lower_logger.distance_from_sea
            up_log_distance = upper_logger.distance_from_sea
            if self.distance_from_sea < low_log_distance:
                self.lower_logger, self.upper_logger = lower_logger, upper_logger
                return
            if low_log_distance <= self.distance_from_sea < up_log_distance:
                self.lower_logger, self.upper_logger = lower_logger, upper_logger
                return

        self.lower_logger, self.upper_logger = lower_logger, upper_logger

    @staticmethod
    def interpolate_water_level(
            lower_level: float,
            upper_level: float,
            x1: float,
            x2: float,
            desired_x: float
    ) -> float:
        water_slope = (lower_level - upper_level) / (x1 - x2)
        y_intercept = upper_level - water_slope * x2
        water_elevation = water_slope * desired_x + y_intercept
        return water_elevation

    def get_water_elevation(self, logger_points: list):
        self.get_loggers_working_at_measurement_time(logger_points)
        self.get_nearest_loggers()
        earlier_time, later_time = self.get_closest_logger_times(
            self.lower_logger
        )
        assert None not in (earlier_time, later_time)
        lower_elevation = self.interpolate_water_level(
            self.lower_logger.logger_data[earlier_time],
            self.lower_logger.logger_data[later_time],
            earlier_time.timestamp(),
            later_time.timestamp(),
            self.measurement_datetime.timestamp()
        )
        earlier_time, later_time = self.get_closest_logger_times(
            self.upper_logger
        )
        assert None not in (earlier_time, later_time)
        upper_elevation = self.interpolate_water_level(
            self.upper_logger.logger_data[earlier_time],
            self.upper_logger.logger_data[later_time],
            earlier_time.timestamp(),
            later_time.timestamp(),
            self.measurement_datetime.timestamp()
        )
        self.water_elevation = self.interpolate_water_level(
            lower_elevation,
            upper_elevation,
            self.lower_logger.distance_from_sea,
            self.upper_logger.distance_from_sea,
            self.distance_from_sea
        )

    def get_bottom_elevation(self):
        self.bottom_elevation = self.water_elevation - self.depth


