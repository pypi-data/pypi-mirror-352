import math
from functools import total_ordering

RHO = 200 / math.pi

@total_ordering
class Angle(object):

    def __init__(self, rad: int = 0):
        self.value_rad = rad

    @staticmethod
    def from_gon(gon_value):
        r = Angle()
        r.set_gon(gon_value)
        return r

    @staticmethod
    def from_rad(rad_value):
        r = Angle(rad_value)
        return r

    def set_gon(self, gon):
        self.value_rad = gon / RHO
        return

    def get_gon(self):
        return self.value_rad * RHO


    def __abs__(self):
        r = Angle()
        r.value_rad = abs(self.value_rad)
        return r

    def __add__(self, o):
        if isinstance(o, Angle):
            r = Angle()
            r.value_rad = self.value_rad + o.value_rad
            return r
        else:
            raise TypeError("unsupported operand type(s) for +: 'Angle' and '" + str(type(o).__name__) + "'")

    def __sub__(self, o):
        if isinstance(o, Angle):
            r = Angle()
            r.value_rad = self.value_rad - o.value_rad
            return r
        else:
            raise TypeError("unsupported operand type(s) for -: 'Angle' and '" + type(o).__name__ + "'")

    def __truediv__(self, o):
        if isinstance(o, (int, float)):
            r = Angle()
            r.value_rad = self.value_rad / o
        else:
            raise TypeError("unsupported operand type(s) for /: 'Angle' and '" + type(o).__name__ + "'")
        return r

    def __eq__(self, other):
        if not isinstance(other, Angle):
            return NotImplemented
        return self.value_rad == other.value_rad

    def __lt__(self, other):
        if not isinstance(other, Angle):
            return NotImplemented
        return self.value_rad < other.value_rad

    def __str__(self):
        return '{0:.7} gon'.format(self.get_gon())

    def normalise(self):
        self.value_rad %= 2 * math.pi
        return self

    def add_half_circle(self):
        r = Angle()
        r.value_rad = self.value_rad + math.pi
        r.normalise()
        return r

    def supplementary_angle(self):
        r = Angle()
        r.value_rad = 2 * math.pi - self.value_rad
        return r

    def sin(self):
        return math.sin(self.value_rad)

    def cos(self):
        return math.cos(self.value_rad)