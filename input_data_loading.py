import argparse
from collections import OrderedDict
import os
import csv

from openpyxl import load_workbook


def get_console_arguments():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        '-b',
        '--bathymetry_directory',
        default='bathymetry_data/',
        help='Enter path of directory containing '
             '*.csv files with bathymetry data.'
    )
    argument_parser.add_argument(
        '-f',
        '--fairway_points_filepath',
        default='fairway_points.csv',
        help='Enter path of *.csv file containing '
             'points located along a fairway.'
    )
    argument_parser.add_argument(
        '-l',
        '--logger_points_filepath',
        default='logger_points.csv',
        help='Enter path of *.csv file containing '
             'points where water elevation measurements provided.'
    )
    argument_parser.add_argument(
        '-x',
        '--logger_data_filepath',
        default='logger_data.xlsx',
        help='Enter path of *.xlsx file containing water elevation data.'
    )
    argument_parser.add_argument(
        '-o',
        '--output_filepath',
        default='output.csv',
        help='Enter path of *.csv file containing the script`s output.'
    )
    arguments = argument_parser.parse_args()
    return arguments


def get_bathymetry_file_paths(directory_path):
    filename_list = []
    for entry in os.scandir(directory_path):
        file_root, file_extension = os.path.splitext(entry.path)
        if file_extension == '.csv':
            filename_list.append(entry.path)
    return filename_list


def get_input_filenames(script_arguments):
    bathymetry_file_paths_list = get_bathymetry_file_paths(
        script_arguments.bathymetry_directory
    )
    # use OrderedDict() instance to correctly extract data
    # from output of "load_input_data()"
    input_csv_filenames = OrderedDict([
        ('bathymetry', bathymetry_file_paths_list),
        ('points_along_fairway', [script_arguments.fairway_points_filepath]),
        ('logger_coordinates', [script_arguments.logger_points_filepath])
    ])
    water_elevation_filename = script_arguments.logger_data_filepath
    return input_csv_filenames, water_elevation_filename


def load_csv_data(file_name_list):
    data_list = []
    try:
        for file_path in file_name_list:
            with open(file_path, 'r', encoding='utf-8') as input_file:
                file_reader = csv.reader(input_file, delimiter=';')
                for row in file_reader:
                    row.append(file_path)
                    data_list.append(row)
        return data_list
    except FileNotFoundError:
        return None


def load_input_data(csv_file_names, xlsx_file_name):
    input_files_content = []
    for file_type in csv_file_names:
        filename_list = csv_file_names[file_type]
        data_of_single_input_type = load_csv_data(filename_list)
        input_files_content.append(data_of_single_input_type)
    try:
        xlsx_workbook = load_workbook(xlsx_file_name, read_only=True)
    except FileNotFoundError:
        xlsx_workbook = None
    input_files_content.append(xlsx_workbook)
    return input_files_content
