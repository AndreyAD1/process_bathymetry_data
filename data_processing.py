import csv
import utm
from math import hypot, inf
from datetime import timedelta
from dateutil.parser import parse
from copy import deepcopy

from input_data_loading import (
    get_console_arguments,
    get_input_filenames,
    load_input_data,
)
from errors_and_warnings import (
    print_about_filenotfounderror_and_exit,
    print_about_wrong_file_format_and_exit,
    print_invalid_points
)
from points import BathymetryPoint


def get_bathymetry_points(point_list):
    bathymetry_list = []
    for point in point_list:
        try:
            long, lat, depth, _, _, _, datetime_str, filepath = point
        except ValueError:
            return None
        try:
            depth = float(depth.replace(',', '.'))
        except ValueError:
            depth = None
        measurement_datetime = parse(
            datetime_str,
            dayfirst=True,
            yearfirst=False
        )
        bathymetry_point = BathymetryPoint(
            float(lat),
            float(long),
            measurement_datetime,
            depth,
            filepath
        )
        bathymetry_list.append(bathymetry_point)
    return bathymetry_list


def get_fairway_points(point_list):
    fairway_list = []
    for point in point_list:
        feature_names = [
            'longitude',
            'latitude',
            'distance_from_seashore',
            'file_name'
        ]
        try:
            longitude, latitude, _, distance, file_name = point
        except ValueError:
            return None
        feature_values = [longitude, latitude, distance, file_name]
        point_dict = dict(zip(feature_names, feature_values))
        fairway_list.append(point_dict)
    return fairway_list


def get_logger_points(point_list):
    logger_list = []
    for point in point_list:
        feature_names = ['longitude', 'latitude', 'logger_name', 'file_name']
        try:
            longitude, latitude, logger_name, file_name = point
        except ValueError:
            return None
        feature_values = [longitude, latitude, logger_name, file_name]
        point_dict = dict(zip(feature_names, feature_values))
        logger_list.append(point_dict)
    return logger_list


def get_logger_data(xlsx_workbook):
    all_loggers_data = {}
    for sheet in xlsx_workbook:
        logger_trace = {}
        for row in sheet.iter_rows(min_row=2, max_col=2):
            measurement_datetime = row[0].value
            if measurement_datetime is None:
                break
            elevation = row[1].value
            logger_trace[measurement_datetime] = elevation
        all_loggers_data[sheet.title] = logger_trace
    return all_loggers_data


def get_data_from_files_content(content):
    bathymetry_data, fairway_data, loggers, xlsx_file_workbook = content
    bathymetry_points = get_bathymetry_points(bathymetry_data)
    fairway_points = get_fairway_points(fairway_data)
    logger_points = get_logger_points(loggers)
    water_elevation_data = get_logger_data(xlsx_file_workbook)
    input_data = [
        bathymetry_points,
        fairway_points,
        logger_points,
        water_elevation_data
    ]
    return input_data


def convert_geocoordinates_to_utm(dataset_list):
    dataset_with_coordinates = deepcopy(dataset_list)
    for dataset in dataset_with_coordinates:
        for point in dataset:
            if not all(point.values()):
                point['longitude'] = None
                point['latitude'] = None
                continue
            longitude = float(point['longitude'])
            latitude = float(point['latitude'])
            utm_long, utm_lat, zone_num, zone_letter = utm.from_latlon(
                latitude, longitude
            )
            point['longitude'] = utm_long
            point['latitude'] = utm_lat
    return dataset_with_coordinates


def round_logger_datetime(logger_data):
    data_with_rounded_time = deepcopy(logger_data)
    for logger in logger_data:
        logger_trace = logger_data[logger]
        rounded_logger_data = {}
        for measurement_datetime, water_elevation in logger_trace.items():
            measurement_datetime += timedelta(seconds=30)
            rounded_datetime = measurement_datetime - timedelta(
                seconds=measurement_datetime.second,
                microseconds=measurement_datetime.microsecond
            )
            rounded_logger_data[rounded_datetime] = water_elevation
        data_with_rounded_time[logger] = rounded_logger_data
    return data_with_rounded_time


def get_distance_to_the_fairway_point(fairway_point, lat, long):
    fairway_point_lat = fairway_point['latitude']
    fairway_point_long = fairway_point['longitude']
    only_numbers = fairway_point_lat and fairway_point_long and lat and long
    if only_numbers:
        distance = hypot(fairway_point_lat - lat, fairway_point_long - long)
        return distance
    return inf


def get_distance_from_sea(points, points_along_fairway):
    points_with_distance_from_sea = deepcopy(points)
    for point in points_with_distance_from_sea:
        if not all(point.values()):
            point['distance_from_seashore'] = None
            continue
        latitude = point['latitude']
        longitude = point['longitude']
        closest_fairway_point = min(
            points_along_fairway,
            key=lambda x: get_distance_to_the_fairway_point(
                x,
                latitude,
                longitude
            )
        )
        distance_from_sea = closest_fairway_point['distance_from_seashore']
        point['distance_from_seashore'] = float(distance_from_sea)
    return points_with_distance_from_sea


def output_result(bathymetry_points, output_path):
    column_names = [
        'longitude',
        'latitude',
        'bottom_elevation',
        'time',
        'water_elevation',
        'depth',
        'distance_from_seashore',
        'filepath',
        'upper_logger',
        'lower_logger'
    ]
    with open(output_path, 'w', newline='', encoding='utf-8') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(column_names)
        for point in bathymetry_points:
            writer.writerow(
                [
                    point.longitude,
                    point.latitude,
                    point.bottom_elevation,
                    point.measurement_datetime,
                    point.water_elevation,
                    point.depth,
                    point.distance_from_sea,
                    point.input_filepath,
                    point.upper_logger_name,
                    point.lower_logger_name
                ]
            )


if __name__ == "__main__":
    console_arguments = get_console_arguments()
    csv_filenames, xlsx_filename = get_input_filenames(console_arguments)
    input_files_content = load_input_data(csv_filenames, xlsx_filename)
    if None in input_files_content:
        print_about_filenotfounderror_and_exit(
            input_files_content,
            csv_filenames,
            xlsx_filename
        )

    input_data = get_data_from_files_content(input_files_content)
    if None in input_data:
        print_about_wrong_file_format_and_exit(
            input_data,
            csv_filenames,
        )
    bathymetry_points, fairway_points, logger_points, water_elevation_data = input_data
    [point.convert_geocoordinates_to_utm() for point in bathymetry_points]
    datasets = [fairway_points, logger_points]
    utm_fairway, utm_loggers = convert_geocoordinates_to_utm(
        datasets
    )
    [point.get_distance_from_sea(utm_fairway) for point in bathymetry_points]
    logger_points = get_distance_from_sea(utm_loggers, utm_fairway)
    water_elevation_data = round_logger_datetime(water_elevation_data)
    switched_off_loggers = []
    for point in bathymetry_points:
        disabled_loggers = point.get_water_elevation(
            logger_points,
            water_elevation_data
        )
        switched_off_loggers.append(disabled_loggers)
    if switched_off_loggers:
        print(
            'WARNING! These loggers have no data for some '
            'measurement time moments: {}'.format(switched_off_loggers)
        )
    [point.get_bottom_elevation() for point in bathymetry_points]
    # print_invalid_points(bathymetry_points_with_bottom_elevation)
    output_result(
        bathymetry_points,
        console_arguments.output_filepath
    )
