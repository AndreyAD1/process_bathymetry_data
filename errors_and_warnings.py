import pprint


class InvalidFile:
    def __init__(self, filename: str, invalid_row: ''):
        self.filename = filename
        self.invalid_row = invalid_row

    def __str__(self):
        return 'Invalid file: {}. Invalid row: {}'.format(
            self.filename,
            self.invalid_row
        )


def print_about_filenotfounderror_and_exit(
        invalid_file_paths,
):
    print('ERROR! Can not find these files:')
    pprint.pprint(invalid_file_paths)
    exit()


def print_about_wrong_file_format(invalid_file_list: list):
    print('WARNING! These files have a wrong format:')
    [print(file) for file in invalid_file_list]


def print_invalid_points(points):
    for point in points:
        if not all(point.values()):
            print('WARNING! Invalid point: {}'.format(point))
