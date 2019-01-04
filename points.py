class Point:
    def __init__(self, x_coord, y_coord):
        self.x = x_coord
        self.y = y_coord


class BathymetryPoint(Point):
    def __init__(
            self,
            x_coordinate,
            y_coordinate,
            datetime,
            depth,
            distance_from_sea=None,
            water_elevation=None,
            bottom_elevation=None
    ):
        super().__init__(x_coordinate, y_coordinate)
        self.measurement_datetime = datetime
        self.depth = depth
        self.distance_from_sea = distance_from_sea
        self.water_elevation = water_elevation
        self.bottom_elevation = bottom_elevation

    def get_distance_from_sea(self):
        self.distance_from_sea = 0

    def get_water_elevation(self):
        self.water_elevation = 0

    def get_bottom_elevation(self):
        self.bottom_elevation = self.water_elevation - self.depth


class LoggerPoint(Point):
    def __init__(
            self,
            logger_name,
            x_coordinate,
            y_coordinate,
            logger_data=None,
            switched_on=True
    ):
        super().__init__(x_coordinate, y_coordinate)
        self.name = logger_name
        self.logger_data = logger_data
        self.switched_on = switched_on

    def get_logger_data(self):
        self.logger_data = []

    def check_switched_on_status(self):
        pass


class FairwayPoint(Point):
    def __init__(self, x_coordinate, y_coordinate, distance_from_sea):
        super().__init__(x_coordinate, y_coordinate)
        self.distance_from_sea = distance_from_sea
