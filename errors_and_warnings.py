

def print_about_filenotfounderror_and_exit(
        input_content,
        csv_filenames,
        xlsx_filename
):
    bathymetry, fairway, logger_data, water_elevation = input_content
    if bathymetry is None:
        exit('Can not find {}'.format(csv_filenames['bathymetry']))
    if fairway is None:
        exit('Can not find {}'.format(csv_filenames['points_along_fairway']))
    if logger_data is None:
        exit('Can not find {}'.format(csv_filenames['logger_coordinates']))
    if water_elevation is None:
        exit('Can not find {}'.format(xlsx_filename))
    return


def print_about_wrong_file_format_and_exit(
        input_data,
        csv_filenames
):
    bathymetry, fairway_info, logger_info, water_elevation_info = input_data
    if bathymetry is None:
        exit(
            'The wrong format of data in some of these files: {}.'.format(
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
    if water_elevation_info is None:
        exit('The wrong format of *.xlsx file.')
    return


def print_invalid_points(points):
    for point in points:
        if not all(point.values()):
            print('WARNING! Invalid point: {}'.format(point))
    return
