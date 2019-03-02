import csv

from dateutil.parser import parse

from input_data_loading import (
    get_console_arguments,
    get_input_filenames,
    load_input_data,
)
from errors_and_warnings import (
    InvalidFile,
    print_about_filenotfounderror_and_exit,
    print_about_wrong_file_format,
    print_invalid_points
)
from points import BathymetryPoint, FairwayPoint, LoggerPoint


def get_bathymetry_points(bathymetry_data: dict) -> tuple:
    bathymetry_list = []
    invalid_files_list = []
    for file, file_content in bathymetry_data.items():
        for point in file_content:
            try:
                long, lat, depth, _, _, _, datetime_str = point
            except ValueError:
                invalid_files_list.append(InvalidFile(file, point))
                break
            try:
                depth = float(depth.replace(',', '.'))
            except ValueError:
                depth = None
            try:
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
                    input_filepath=file
                )
            except ValueError:
                invalid_files_list.append(InvalidFile(file, point))
                break
            bathymetry_list.append(bathymetry_point)
    return bathymetry_list, invalid_files_list


def get_fairway_points(input_fairway_data):
    fairway_list = []
    invalid_files_list = []
    for file_name, point_list in input_fairway_data.items():
        for point in point_list:
            try:
                longitude, latitude, _, distance = point
            except ValueError:
                invalid_files_list.append(InvalidFile(file_name, point))
                break
            fairway_point = FairwayPoint(
                float(latitude),
                float(longitude),
                float(distance),
                file_name
            )
            fairway_list.append(fairway_point)
    return fairway_list, invalid_files_list


def get_logger_points(
        input_logger_data: dict,
        all_loggers_data: dict
) -> tuple:
    logger_list = []
    invalid_files_list = []
    for file_name, point_list in input_logger_data.items():
        for point in point_list:
            try:
                longitude, latitude, logger_name = point
            except ValueError:
                invalid_files_list.append(InvalidFile(file_name, point))
                break
            logger_data = all_loggers_data[logger_name]
            logger_point = LoggerPoint(
                logger_name,
                float(latitude),
                float(longitude),
                input_filepath=file_name,
                logger_data=logger_data
            )
            logger_list.append(logger_point)
    return logger_list, invalid_files_list


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
    bathymetry_points, invalid_files = get_bathymetry_points(bathymetry_data)
    fairway_points, invalid_fairway_files = get_fairway_points(fairway_data)
    water_elevation_data = get_logger_data(xlsx_file_workbook)
    logger_points, invalid_log_files = get_logger_points(
        loggers,
        water_elevation_data
    )
    input_data = [bathymetry_points, fairway_points, logger_points]
    invalid_files = invalid_files + invalid_fairway_files + invalid_log_files
    return input_data, invalid_files


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
                    round(point.bottom_elevation, 2),
                    point.measurement_datetime,
                    round(point.water_elevation, 2),
                    round(point.depth, 2),
                    point.distance_from_sea,
                    point.input_filepath,
                    point.upper_logger.logger_name,
                    point.lower_logger.logger_name
                ]
            )


if __name__ == "__main__":
    console_arguments = get_console_arguments()
    csv_filenames, xlsx_filename = get_input_filenames(console_arguments)
    input_files_content, invalid_filepaths = load_input_data(
        csv_filenames,
        xlsx_filename
    )
    if invalid_filepaths:
        print_about_filenotfounderror_and_exit(invalid_filepaths)

    input_data, invalid_files = get_data_from_files_content(input_files_content)

    if invalid_files:
        print_about_wrong_file_format(invalid_files)

    bathymetry_points, fairway_points, logger_points = input_data
    [point.convert_geocoordinates_to_utm() for point in bathymetry_points]
    [point.convert_geocoordinates_to_utm() for point in fairway_points]
    [point.convert_geocoordinates_to_utm() for point in logger_points]
    [point.get_distance_from_sea(fairway_points) for point in bathymetry_points]
    [point.get_distance_from_sea(fairway_points) for point in logger_points]
    [point.get_water_elevation(logger_points) for point in bathymetry_points]
    for point in bathymetry_points:
        if point.switched_off_loggers:
            print(
                """
                WARNING! 
                These loggers have no data for the point measured at {}
                (from the input file {}): 
                {}""".format(
                    point.measurement_datetime,
                    point.input_filepath,
                    [l.logger_name for l in point.switched_off_loggers]
                )
            )
    [point.get_bottom_elevation() for point in bathymetry_points]
    # print_invalid_points(bathymetry_points_with_bottom_elevation)
    output_result(
        bathymetry_points,
        console_arguments.output_filepath
    )
