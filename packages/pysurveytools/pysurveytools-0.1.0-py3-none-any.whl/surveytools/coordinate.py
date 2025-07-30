import math

from surveytools.angle import Angle


class Coordinate(object):

    def __init__(self, pkt_nr : str, x: float, y: float, z: float):
        self.value_rad = None
        self.pkt_nr = pkt_nr
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, o):
        if isinstance(o, Coordinate):
            return Coordinate(self.pkt_nr, self.x + o.x, self.y + o.y, self.z + o.z)
        else:
            raise TypeError("unsupported operand type(s) for +: 'Coordinate' and '" + type(o).__name__ + "'")

    def __sub__(self, o):
        if isinstance(o, Coordinate):
            return Coordinate(self.pkt_nr, self.x - o.x, self.y - o.y, self.z - o.z)
        else:
            raise TypeError("unsupported operand type(s) for -: 'Coordinate' and '" + type(o).__name__ + "'")

    def direction_to(self, o):
        dc = o - self
        theta_rad = math.atan2(dc.x, dc.y)
        return Angle.from_rad(theta_rad)

    def distance_to(self, o):
        dc = o - self
        return math.sqrt(dc.x * dc.x + dc.y * dc.y + dc.z * dc.z)

    def get_array(self):
        return [self.y, self.x, self.z]

    def get_homogene_array(self):
        return [self.y, self.x, self.z, 1]

    def get_normalized_vector(self):
        norm = math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
        return [self.x / norm, self.y / norm, self.z / norm]

    def __str__(self):
        return f"[Pkt: {self.pkt_nr}, x: {self.x:.4f}, y: {self.y:.4f}, z: {self.z:.4f}]"