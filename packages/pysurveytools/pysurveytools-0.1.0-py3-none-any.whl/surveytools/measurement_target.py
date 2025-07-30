from surveytools.angle import Angle
from surveytools.measurement import Measurement


class MeasurementTarget(object):
    def __init__(self, target: str, direction: Angle, zenith: Angle, distance: float):
        self.target_number = target
        self.direction = direction
        self.distance = distance
        self.zenith = zenith
        self.face1 = []
        self.face2 = []

    def evaluation(self, zero_direction: Angle = Angle.from_rad(0)) -> Measurement:
        return Measurement(self.target_number, self.direction_evaluation(zero_direction), self.zenith_evaluation(), self.distance_evaluation(), self.face1[0].atmospheric_data, self.face1[0].measure_time)

    def direction_evaluation(self, zero_direction : Angle) -> Angle:
        sum_r = Angle()
        for i in range(len(self.face1)):
            sum_r += ((self.face1[i].direction + self.face2[i].direction.add_half_circle())/2.0 - zero_direction).normalise()
        return sum_r/len(self.face1)

    def zenith_evaluation(self) -> Angle:
        sum_z = Angle()
        for i in range(len(self.face1)):
            sum_z += (((self.face1[i].zenith - self.face2[i].zenith).normalise()) / 2.0)
        return sum_z / len(self.face1)

    def distance_evaluation(self) -> float:
        sum_d = 0
        for i in range(len(self.face1)):
            sum_d += (self.face1[i].slope_distances + self.face2[i].slope_distances) / 2.0
        return sum_d / len(self.face1)

    def __str__(self):
        return "Target: " +  str(self.target_number) + " hz: " + str(self.direction) + " vz: " + str(self.zenith) + " s: " + str(self.distance)