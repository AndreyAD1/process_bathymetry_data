import csv
from math import hypot, inf
import utm
from openpyxl import load_workbook
from collections import OrderedDict
from datetime import datetime, timedelta
import os


def get_bathymetry_file_paths():
    filenames_list = []
    for entry in os.scandir('bathymetry_data/'):
        file_root, file_extension = os.path.splitext(entry.path)
        if file_extension == '.csv':
            filenames_list.append(entry.path)
    return filenames_list


def load_csv_data(file_name_list):
    try:
        for file_name in file_name_list:
            data_list = []
            with open(file_name, 'r', newline='', encoding='utf-8') as input_file:
                file_reader = csv.reader(input_file, delimiter=';')
                for row in file_reader:
                    data_list.append(row)
        return data_list
    except FileNotFoundError:
        return None


def load_input_data(csv_file_names, xlsx_file_name):
    csv_files_content = []
    for file_type in csv_file_names:
        csv_data = load_csv_data(csv_file_names[file_type])
        csv_files_content.append(csv_data)
    try:
        xlsx_workbook = load_workbook(xlsx_file_name, read_only=True)
    except FileNotFoundError:
        xlsx_workbook = None
    return csv_files_content, xlsx_workbook


def get_bathymetry_points(point_list):
    bathymetry_list = []
    for point in point_list:
        feature_names = ['longitude', 'latitude', 'depth', 'time']
        try:
            longitude, latitude, depth, id1, id2, id3, time, start_time = point
            # print(longitude, latitude, depth, id1, id2, id3, time, start_time)
        except ValueError:
            return None
        try:
            depth = float(depth.replace(',', '.'))
        except ValueError:
            depth = None
        feature_values = [longitude, latitude, depth, time]
        point_dict = dict(zip(feature_names, feature_values))
        bathymetry_list.append(point_dict)
    return bathymetry_list


def get_fairway_points(point_list):
    fairway_list = []
    for point in point_list:
        feature_names = ['longitude', 'latitude', 'distance_from_seashore']
        try:
            longitude, latitude, id, distance = point
        except ValueError:
            return None
        feature_values = [longitude, latitude, distance]
        point_dict = dict(zip(feature_names, feature_values))
        fairway_list.append(point_dict)
    return fairway_list


def get_logger_points(point_list):
    logger_list = []
    for point in point_list:
        feature_names = ['longitude', 'latitude', 'logger_name']
        try:
            longitude, latitude, logger_name = point
        except ValueError:
            return None
        feature_values = [longitude, latitude, logger_name]
        point_dict = dict(zip(feature_names, feature_values))
        logger_list.append(point_dict)
    return logger_list


def get_logger_data(xlsx_workbook):
    all_loggers_data = {}
    for sheet in xlsx_workbook:
        logger_trace = {}
        for row in sheet.iter_rows(min_row=2, max_col=2):
            measurement_datetime = row[0].value
            elevation = row[1].value
            logger_trace[measurement_datetime] = elevation
        all_loggers_data[sheet.title] = logger_trace
    return all_loggers_data


def convert_geocoordinates_to_utm(dataset_list):
    for dataset in dataset_list:
        for point in dataset:
            try:
                longitude = float(point['longitude'])
                latitude = float(point['latitude'])
            except ValueError:
                point['longitude'] = None
                point['latitude'] = None
                continue
            utm_long, utm_lat, zone_num, zone_letter = utm.from_latlon(
                latitude, longitude
            )
            point['longitude'] = utm_long
            point['latitude'] = utm_lat
    return dataset_list


def round_logger_datetime(logger_data):
    for logger in logger_data:
        logger_trace = logger_data[logger]
        rounded_logger_data = {}
        for measurement_datetime, water_elevation in logger_trace.items():
            measurement_datetime += timedelta(seconds=30)
            rounded_datetime = measurement_datetime-timedelta(
                seconds=measurement_datetime.second,
                microseconds=measurement_datetime.microsecond
            )
            rounded_logger_data[rounded_datetime] = water_elevation
        logger_data[logger] = rounded_logger_data
    return logger_data


def get_distance_to_the_fairway_point(fairway_point, lat, long):
    fairway_point_lat = fairway_point['latitude']
    fairway_point_long = fairway_point['longitude']
    only_floats = fairway_point_lat and fairway_point_long and lat and long
    if only_floats:
        distance = hypot(fairway_point_lat - lat, fairway_point_long - long)
        return distance
    return inf


def get_distance_from_sea(points, fairway_points):
    for point in points:
        latitude = point['latitude']
        longitude = point['longitude']
        closest_fairway_point = min(
            fairway_points,
            key=lambda x: get_distance_to_the_fairway_point(
                x,
                latitude,
                longitude
            )
        )
        distance_from_sea = closest_fairway_point['distance_from_seashore']
        point['distance_from_seashore'] = float(distance_from_sea)
    return points


def get_nearest_loggers(distance_from_seashore, logger_list):
    logger_list.sort(key=lambda x: x['distance_from_seashore'])
    previous_logger = logger_list[0]
    for logger in logger_list:
        lower_logger = logger
        upper_logger = logger
        logger_distance = logger['distance_from_seashore']
        if logger_distance >= distance_from_seashore:
            lower_logger = previous_logger
            return lower_logger, upper_logger
        previous_logger = logger
    return lower_logger, upper_logger


def interpolate_water_surface(
        lower_level,
        upper_level,
        lower_distance,
        upper_distance,
        measurement_distance
):
    water_slope = (lower_level-upper_level)/(lower_distance-upper_distance)
    y_intercept = upper_level - water_slope*upper_distance
    water_elevation = water_slope * measurement_distance + y_intercept
    return water_elevation


def get_water_elevation(bathymetry, logger_points, logger_traces):
    for measurement_point in bathymetry:
        lower_log, upper_log = get_nearest_loggers(
            measurement_point['distance_from_seashore'],
            logger_points
        )
        try:
            measurement_time = datetime.strptime(
                measurement_point['time'],
                '%d.%m.%Y %H:%M'
            )
        except ValueError:
            measurement_time = datetime.strptime(
                measurement_point['time'],
                '%d.%m.%y %H:%M'
            )
        lower_log_name = lower_log['logger_name']
        upper_log_name = upper_log['logger_name']
        try:
            lower_elevation = logger_traces[lower_log_name][measurement_time]
            upper_elevation = logger_traces[upper_log_name][measurement_time]
        except KeyError:
            measurement_point['water_elevation'] = None
            continue
        water_elevation = interpolate_water_surface(
            lower_elevation,
            upper_elevation,
            lower_log['distance_from_seashore'],
            upper_log['distance_from_seashore'],
            measurement_point['distance_from_seashore']
        )
        measurement_point['water_elevation'] = water_elevation
    return bathymetry


def get_bottom_elevation(bathymetry):
    for point in bathymetry:
        water_elevation = point['water_elevation']
        depth = point['depth']
        bottom_elevation = water_elevation - depth
        point['bottom_elevation'] = bottom_elevation
    return bathymetry


def print_about_FileNotFoundError_and_exit(
        bathymetry,
        fairway_points,
        logger_points,
        water_elevation_info,
        csv_filenames,
        xlsx_filename
):
    if bathymetry is None:
        exit('Can not find {}.'.format(csv_filenames['bathymetry']))
    if fairway_points is None:
        exit('Can not find {}.'.format(csv_filenames['points_along_fairway']))
    if logger_points is None:
        exit('Can not find {}.'.format(csv_filenames['logger_coordinates']))
    if water_elevation_info is None:
        exit('Can not find {}.'.format(xlsx_filename))
    return


def print_about_wrong_file_format_and_exit(
        bathymetry,
        fairway_info,
        logger_info,
        csv_filenames
):
    if bathymetry is None:
        exit(
            'The wrong format of data in {}.'.format(
                csv_filenames['bathymetry']
            )
        )
    if fairway_info is None:
        exit(
            'The wrong format of data in {}'.format(
                csv_filenames['points_along_fairway']
            )
        )
    if logger_info is None:
        exit(
            'The wrong format of data in {}'.format(
                csv_filenames['logger_coordinates']
            )
        )
    return


def output_result(bathymetry_info):
    field_names = [
        'longitude',
        'latitude',
        'bottom_elevation',
        'time',
        'water_elevation',
        'depth',
        'distance_from_seashore'
    ]
    with open('output.csv', 'w', newline='', encoding='utf-8') as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=field_names,
            delimiter=';'
        )
        writer.writeheader()
        for point in bathymetry_info:
            writer.writerow(point)


if __name__ == "__main__":
    bathymetry_file_paths_list = get_bathymetry_file_paths()
    input_csv_filenames = OrderedDict([
        ('bathymetry', bathymetry_file_paths_list),
        ('points_along_fairway', ['fairway_points.csv']),
        ('logger_coordinates', ['logger_points.csv'])
    ])
    water_elevation_filename = 'logger_data.xlsx'
    csv_files_content, xlsx_file_workbook = load_input_data(
        input_csv_filenames,
        water_elevation_filename
    )
    bathymetry_data, fairway_data, loggers = csv_files_content
    print_about_FileNotFoundError_and_exit(
        bathymetry_data,
        fairway_data,
        loggers,
        xlsx_file_workbook,
        input_csv_filenames,
        water_elevation_filename
    )
    bathymetry_points = get_bathymetry_points(bathymetry_data)
    fairway_points = get_fairway_points(fairway_data)
    logger_points = get_logger_points(loggers)
    water_elevation_data = get_logger_data(xlsx_file_workbook)
    print_about_wrong_file_format_and_exit(
        bathymetry_points,
        fairway_points,
        logger_points,
        input_csv_filenames,
    )
    utm_bathymetry, utm_fairway, utm_loggers = convert_geocoordinates_to_utm([
        bathymetry_points,
        fairway_points,
        logger_points
    ])
    bathymetry_points = get_distance_from_sea(utm_bathymetry, utm_fairway)
    logger_points = get_distance_from_sea(utm_loggers, utm_fairway)
    water_elevation_data = round_logger_datetime(water_elevation_data)
    bathymetry_points = get_water_elevation(
        bathymetry_points,
        logger_points,
        water_elevation_data
    )
    bathymetry_points_with_bottom_elevation = get_bottom_elevation(
        bathymetry_points
    )

    # output = prepare_output(bathymetry_points_with_bottom_elevation)

    output_result(bathymetry_points_with_bottom_elevation)
