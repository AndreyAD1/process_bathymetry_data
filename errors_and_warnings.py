import pprint


class InvalidFile:
    def __init__(self, filename: str, invalid_row: ''):
        self.filename = filename
        self.invalid_row = invalid_row

    def print_invalid_string(self):
        print('The file {} contains an invalid string: {}').format(
            self.filename,
            self.invalid_row
        )


def print_about_filenotfounderror_and_exit(
        invalid_file_paths,
):
    print('ERROR. Can not find these files:')
    pprint.pprint(invalid_file_paths)
    exit()


def print_about_wrong_file_format_and_exit(invalid_file_list: list):
    print('ERROR. These files have a wrong format:')
    for file in invalid_file_list:
        print('Invalid file: {}. Invalid row: {}'.format(
            file.filename,
            file.invalid_row)
        )


def print_invalid_points(points):
    for point in points:
        if not all(point.values()):
            print('WARNING! Invalid point: {}'.format(point))
