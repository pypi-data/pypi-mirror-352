from surveytools.angle import Angle


class FullAngleMeasurement(object):

    def __init__(self):
        self.hz: Angle = Angle()
        self.v: Angle = Angle()
        self.angle_accuracy: Angle = Angle()
        self.angle_time: int = 0
        self.cross_incline: Angle = Angle()
        self.length_incline: Angle = Angle()
        self.accuracy_incline: Angle = Angle()
        self.incline_time: int = 0
        self.face_def: int = 0

    def __str__(self):
        return "[hz: " + str(self.hz) + ", v: " + str(self.v) + " , angle_accuracy: " + str(self.angle_accuracy) + \
               ", angle_time: " + str(self.angle_time) + ", cross_incline: " + str(self.cross_incline) +\
               ", length_incline: " + str(self.length_incline) + ", accuracy_incline: " + str(self.accuracy_incline) + "]"
