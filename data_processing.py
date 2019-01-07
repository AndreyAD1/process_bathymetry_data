import csv
from dateutil.parser import parse

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
from points import BathymetryPoint, FairwayPoint, LoggerPoint


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
            input_filepath=filepath
        )
        bathymetry_list.append(bathymetry_point)
    return bathymetry_list


def get_fairway_points(point_list):
    fairway_list = []
    for point in point_list:
        try:
            longitude, latitude, _, distance, file_name = point
        except ValueError:
            return None
        fairway_point = FairwayPoint(
            float(latitude),
            float(longitude),
            float(distance),
            file_name
        )
        fairway_list.append(fairway_point)
    return fairway_list


def get_logger_points(point_list, all_loggers_data):
    logger_list = []
    for point in point_list:
        try:
            longitude, latitude, logger_name, file_name = point
        except ValueError:
            return None
        logger_data = all_loggers_data[logger_name]
        logger_point = LoggerPoint(
            logger_name,
            float(latitude),
            float(longitude),
            input_filepath=file_name,
            logger_data=logger_data
        )
        logger_list.append(logger_point)
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
    water_elevation_data = get_logger_data(xlsx_file_workbook)
    logger_points = get_logger_points(loggers, water_elevation_data)
    input_data = [
        bathymetry_points,
        fairway_points,
        logger_points,
    ]
    return input_data


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
                    point.upper_logger.logger_name,
                    point.lower_logger.logger_name
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
    bathymetry_points, fairway_points, logger_points = input_data
    [point.convert_geocoordinates_to_utm() for point in bathymetry_points]
    [point.convert_geocoordinates_to_utm() for point in fairway_points]
    [point.convert_geocoordinates_to_utm() for point in logger_points]
    [point.get_distance_from_sea(fairway_points) for point in bathymetry_points]
    [point.get_distance_from_sea(fairway_points) for point in logger_points]
    [point.round_logger_datetime() for point in logger_points]
    [point.get_water_elevation(logger_points) for point in bathymetry_points]
    for point in bathymetry_points:
        if point.switched_off_loggers:
            print(
                """
                WARNING! 
                These loggers have no data for the point measured at {}
                (from the input file {}): {}
                """.format(
                    point.measurement_datetime,
                    point.input_filepath,
                    point.switched_off_loggers
                )
            )
    [point.get_bottom_elevation() for point in bathymetry_points]
    # print_invalid_points(bathymetry_points_with_bottom_elevation)
    output_result(
        bathymetry_points,
        console_arguments.output_filepath
    )
