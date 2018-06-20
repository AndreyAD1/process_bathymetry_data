from csv import reader
from math import hypot
import utm
from openpyxl import load_workbook


def get_input_data(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as input_file:
            file_reader = reader(input_file, delimiter=';')
            data_list = []
            for row in file_reader:
                data_list.append(row)
            return data_list
    except FileNotFoundError:
        return None


def make_bathymetry_list(point_list):
    bathymetry_list = []
    for point in point_list:
        feature_names = ['longitude', 'latitude', 'depth', 'time']
        try:
            longitude, latitude, depth, id1, id2, id3, time, start_time = point
        except ValueError:
            return None
        depth = float(depth.replace(',', '.'))
        feature_values = [longitude, latitude, depth, time]
        point_dict = dict(zip(feature_names, feature_values))
        bathymetry_list.append(point_dict)
    return bathymetry_list


def make_fairway_list(point_list):
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


def make_logger_list(point_list):
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


def convert_geocoordinates_to_utm(points):
    for point in points:
        longitude = float(point['longitude'])
        latitude = float(point['latitude'])
        utm_longitude, utm_latitude, zone_num, zone_letter = utm.from_latlon(
            latitude, longitude
        )
        point['longitude'] = utm_longitude
        point['latitude'] = utm_latitude
    return points


def get_distance_to_the_fairway_point(fairway_point, lat, long):
    fairway_point_lat = fairway_point['latitude']
    fairway_point_long = fairway_point['longitude']
    distance = hypot(fairway_point_lat - lat, fairway_point_long - long)
    return distance


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


def get_water_elevation(measurement_point, logger_points):
    nearest_loggers = get_nearest_loggers(
        measurement_point['distance_from_seashore'],
        logger_points
    )
    # print(nearest_loggers)
    # point_time = get_point_time()
    # get_logger_water_elevations(point_time)
    # pass
    return 0


def get_bottom_elevation(bathymetry_points, water_elevation_points):
    for point in bathymetry_points:
        water_elevation = get_water_elevation(point, water_elevation_points)
        depth = point['depth']
        bottom_elevation = water_elevation - depth
        point['bottom_elevation'] = bottom_elevation
    return bathymetry_points


def output_result():
    pass


if __name__ == "__main__":
    bathymetry_data = get_input_data('bathymetry.csv')
    fairway_data = get_input_data('fairway_points.csv')
    logger_data = get_input_data('logger_points.csv')
    if bathymetry_data is None:
        exit('Can non find the file containing bathymetry data.')
    if fairway_data is None:
        exit('Can not find the file containing points along the fairway.')
    if logger_data is None:
        exit('Can not find the file containing logger coordinates.')
    water_elevation_data = load_workbook('logger_data.xlsx', read_only=True)
    # logger0 = water_elevation_data['0']
    # for row in range(1, 20):
    #     datetime = logger0.cell(column=1, row=row).value
    #     water_elevation = logger0.cell(column=2, row=row).value
    #     print(datetime, water_elevation)

    bathymetry_list_of_dicts = make_bathymetry_list(bathymetry_data)
    fairway_list_of_dicts = make_fairway_list(fairway_data)
    logger_list_of_dicts = make_logger_list(logger_data)
    if bathymetry_list_of_dicts is None:
        exit(
            'The wrong format of data in the file containing bathymetry data.'
        )
    if fairway_list_of_dicts is None:
        exit(
            'The wrong format of data in the file containing points '
            'along the fairway.'
        )
    if logger_list_of_dicts is None:
        exit(
            'The wrong format of data in the file containing '
            'logger coordinates.'
        )

    utm_bathymetry = convert_geocoordinates_to_utm(bathymetry_list_of_dicts)
    utm_fairway = convert_geocoordinates_to_utm(fairway_list_of_dicts)
    utm_loggers = convert_geocoordinates_to_utm(logger_list_of_dicts)
    print(utm_loggers)
    bathymetry_points_with_distance_from_sea = get_distance_from_sea(
        utm_bathymetry,
        utm_fairway
    )
    logger_points_with_distance_from_sea = get_distance_from_sea(
        utm_loggers,
        utm_fairway
    )

    print(logger_points_with_distance_from_sea)
    bathymetry_points_with_bottom_elevation = get_bottom_elevation(
        bathymetry_points_with_distance_from_sea,
        logger_points_with_distance_from_sea
    )
    print(bathymetry_points_with_bottom_elevation)
    output_result()
