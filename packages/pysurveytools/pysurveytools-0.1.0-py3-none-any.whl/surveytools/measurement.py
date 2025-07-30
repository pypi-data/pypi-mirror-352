from surveytools.coordinate import Coordinate
from surveytools.angle import Angle


class Measurement(object):

    def __init__(self, target : str, direction: Angle, zenith: Angle, sd : float, atmospheric_data, measure_time):
        self.target_number = target
        self.direction = direction
        self.zenith = zenith
        self.slope_distances = sd
        self.atmospheric_data = atmospheric_data
        self.measure_time = measure_time

    def __str__(self):
        return "[target: " + str(self.target_number) + ", direction: " + str(self.direction) + " , zenith: " \
               + str(self.zenith) + ", slope_distances: " + str(self.slope_distances) + ", atmospheric_data: "\
               + str(self.atmospheric_data) + ", Measure Time: " + str(self.measure_time) + "]"

    def get_horizontal_distances(self):
        return self.slope_distances * self.zenith.sin()

    def get_delta_height(self):
        return self.slope_distances * self.zenith.cos()

    def get_local_coordinate(self):
        hd = self.get_horizontal_distances()
        y = hd * self.direction.sin()
        x = hd * self.direction.cos()
        z = self.get_delta_height()
        return Coordinate(self.target_number, x, y, z)

    def get_arra(self):
        return [self.target_number, self.direction.get_gon(), self.zenith.get_gon(), self.slope_distances ]