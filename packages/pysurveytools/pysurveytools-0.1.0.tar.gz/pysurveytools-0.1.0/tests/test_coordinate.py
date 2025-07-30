# tests/test_coordinate.py

import math
import pytest
from surveytools import Angle, Coordinate


def test_add_and_subtract_coordinates():
    a = Coordinate("A", 1.0, 2.0, 3.0)
    b = Coordinate("B", 4.0, 5.0, 6.0)
    # Addition
    c = a + b
    assert isinstance(c, Coordinate)
    assert c.pkt_nr == "A"
    assert c.x == pytest.approx(5.0)
    assert c.y == pytest.approx(7.0)
    assert c.z == pytest.approx(9.0)
    # Subtraktion
    d = b - a
    assert isinstance(d, Coordinate)
    assert d.pkt_nr == "B"
    assert d.x == pytest.approx(3.0)
    assert d.y == pytest.approx(3.0)
    assert d.z == pytest.approx(3.0)
    # Falsche Operanden-Typen werfen TypeError
    with pytest.raises(TypeError):
        _ = a + 123
    with pytest.raises(TypeError):
        _ = b - "foo"

def test_direction_to_and_distance_to():
    origin = Coordinate("O", 0.0, 0.0, 0.0)
    # Punkt auf der X-Achse
    p1 = Coordinate("P1", 1.0, 0.0, 0.0)
    ang = origin.direction_to(p1)
    # math.atan2(dc.x, dc.y) für dc=(1,0,0) ergibt π/2
    assert isinstance(ang, Angle)
    assert ang.value_rad == pytest.approx(math.pi/2)
    # Abstand sollte 1.0 sein
    assert origin.distance_to(p1) == pytest.approx(1.0)
    # 3–4–12–Triangle: sqrt(9+16+144) = 13
    p2 = Coordinate("P2", 3.0, 4.0, 12.0)
    assert origin.distance_to(p2) == pytest.approx(13.0)

def test_array_methods_and_normalized_vector():
    p = Coordinate("P", 1.1, 2.2, 3.3)
    # get_array gibt [y, x, z]
    assert p.get_array() == [2.2, 1.1, 3.3]
    # homogene Koordinaten
    assert p.get_homogene_array() == [2.2, 1.1, 3.3, 1]
    # Normalisierter Vektor
    norm = math.sqrt(1.1**2 + 2.2**2 + 3.3**2)
    vec = p.get_normalized_vector()
    assert vec[0] == pytest.approx(1.1 / norm)
    assert vec[1] == pytest.approx(2.2 / norm)
    assert vec[2] == pytest.approx(3.3 / norm)

def test_str_representation():
    # Die __str__-Methode solltePkt-Nummer und gerundete Werte anzeigen
    p = Coordinate("X1", 1.23456, 2.34567, 3.45678)
    s = str(p)
    assert s.startswith("[Pkt: X1")
    # Je nach implementiertem Format auf 4 Dezimalstellen gerundet
    assert "x: 1.2346" in s
    assert "y: 2.3457" in s
    assert "z: 3.4568" in s
