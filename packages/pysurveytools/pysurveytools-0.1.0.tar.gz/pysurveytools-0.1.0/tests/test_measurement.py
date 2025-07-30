# tests/test_measurement.py

import math
import pytest
from surveytools import Angle, Coordinate, Measurement


def test_init_and_attributes():
    atm = {"pressure": 1013.25, "temp": 20.0}
    mt = "2025-05-26T12:00:00"
    m = Measurement(42, Angle.from_gon(100), Angle.from_rad(math.pi / 4), 123.45, atm, mt)

    # Attribute wurden korrekt gesetzt
    assert m.target_number == 42
    assert m.direction.get_gon() == pytest.approx(100)  # Gauge aus Gon :contentReference[oaicite:0]{index=0}
    assert m.zenith.value_rad == pytest.approx(
        math.pi / 4)  # Radiant direkt aus from_rad :contentReference[oaicite:1]{index=1}
    assert m.slope_distances == pytest.approx(123.45)
    assert m.atmospheric_data is atm
    assert m.measure_time == mt


def test_get_horizontal_distances():
    # hd = slope_distances * sin(zenith)
    zen = Angle.from_rad(math.pi / 6)
    m = Measurement(0, Angle.from_rad(0), zen, 10.0, None, None)
    expected = 10.0 * math.sin(math.pi / 6)
    assert m.get_horizontal_distances() == pytest.approx(
        expected)  # get_horizontal_distances :contentReference[oaicite:2]{index=2}


def test_get_delta_height():
    # dh = slope_distances * cos(zenith)
    zen = Angle.from_rad(math.pi / 3)
    m = Measurement(0, Angle.from_rad(0), zen, 20.0, None, None)
    expected = 20.0 * math.cos(math.pi / 3)
    assert m.get_delta_height() == pytest.approx(expected)  # get_delta_height :contentReference[oaicite:3]{index=3}


def test_get_local_coordinate():
    # hd = sd * sin(zenith) = 5 * 1 = 5
    # direction = 45° → x = hd*cos(45°), y = hd*sin(45°), z = sd*cos(zenith) = 0
    dir_ang = Angle.from_rad(math.pi / 4)
    zen = Angle.from_rad(math.pi / 2)
    m = Measurement(7, dir_ang, zen, 5.0, None, None)
    coord = m.get_local_coordinate()

    assert isinstance(coord, Coordinate)
    assert coord.pkt_nr == 7
    assert coord.x == pytest.approx(
        5.0 * math.cos(math.pi / 4))  # get_local_coordinate :contentReference[oaicite:4]{index=4}
    assert coord.y == pytest.approx(5.0 * math.sin(math.pi / 4))
    assert coord.z == pytest.approx(5.0 * math.cos(math.pi / 2))


def test_get_arra_and_str():
    # get_arra liefert [target_number, direction_gon, zenith_gon, slope_distances]
    dir_ang = Angle.from_gon(150)
    zen = Angle.from_gon(75)
    m = Measurement(8, dir_ang, zen, 12.3, "ATM_DATA", "TIME_STAMP")
    arr = m.get_arra()
    assert arr == [8, pytest.approx(dir_ang.get_gon()), pytest.approx(zen.get_gon()),
                   pytest.approx(12.3)]  # get_arra :contentReference[oaicite:5]{index=5}

    # __str__ enthält alle Informationen
    s = str(m)
    assert "target: 8" in s
    assert "direction:" in s and "gon" in s
    assert "zenith:" in s and "gon" in s
    assert "slope_distances: 12.3" in s
    assert "atmospheric_data: ATM_DATA" in s
    assert "Measure Time: TIME_STAMP" in s  # __str__ :contentReference[oaicite:6]{index=6}
