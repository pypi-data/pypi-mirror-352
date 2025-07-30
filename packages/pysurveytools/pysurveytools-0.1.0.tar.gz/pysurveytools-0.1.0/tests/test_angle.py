import math
import pytest
from surveytools import RHO, Angle


@pytest.mark.parametrize("gon", [0, 50, 200])
def test_from_and_to_gon(gon):
    a = Angle.from_gon(gon)
    assert pytest.approx(a.get_gon(), rel=1e-9) == gon

def test_conversion_rad_gon():
    rad = math.pi
    a = Angle.from_rad(rad)
    assert pytest.approx(a.get_gon(), rel=1e-9) == rad * RHO

def test_normalise_wraps():
    a = Angle.from_rad(3 * math.pi)
    a.normalise()
    assert pytest.approx(a.value_rad, rel=1e-9) == math.pi

@pytest.mark.parametrize("a_gon,b_gon,expected", [
    (100, 100, True),
    ( 50,100, False),
])
def test_eq(a_gon, b_gon, expected):
    a = Angle.from_gon(a_gon)
    b = Angle.from_gon(b_gon)
    assert (a == b) is expected
    assert (a != b) is (not expected)

@pytest.mark.parametrize("a_rad,b_rad,expected", [
    (1.0, 2.0, True),
    (2.0, 1.0, False),
    ( math.pi, math.pi, False),
])
def test_lt(a_rad, b_rad, expected):
    a = Angle.from_rad(a_rad)
    b = Angle.from_rad(b_rad)
    assert (a < b) is expected
    assert (b > a) is expected  # test __gt__

@pytest.mark.parametrize("a_rad,b_rad,expected", [
    (1.0, 1.0, True),
    (1.0, 2.0, True),
    (2.0, 1.0, False),
])
def test_le(a_rad, b_rad, expected):
    a = Angle.from_rad(a_rad)
    b = Angle.from_rad(b_rad)
    assert (a <= b) is expected
    assert (b >= a) is expected  # test __ge__

def test_sin_cos():
    # sin und cos für 30° (π/6)
    a = Angle.from_rad(math.pi / 6)
    assert pytest.approx(a.sin(), rel=1e-9) == 0.5
    assert pytest.approx(a.cos(), rel=1e-9) == math.sqrt(3) / 2

def test_supplementary_angle():
    # 2π – π/2 = 3π/2
    a = Angle.from_rad(math.pi / 2)
    sup = a.supplementary_angle()
    assert pytest.approx(sup.value_rad, rel=1e-9) == 2 * math.pi - math.pi / 2

def test_add_half():
    a = Angle.from_rad(1.0)
    half = a.add_half_circle()
    # prüfe reinen Wert
    assert pytest.approx(half.value_rad, rel=1e-9) == 1.0 + math.pi


def test_add_and_subtract_angles():
    a = Angle.from_rad(1.5)
    b = Angle.from_rad(2.5)
    c = a + b
    d = b - a

    assert pytest.approx(c.value_rad, rel=1e-9) == 4.0
    assert pytest.approx(d.value_rad, rel=1e-9) == 1.0

def test_division_by_scalar():
    a = Angle.from_rad(2.0)
    half = a / 2
    assert pytest.approx(half.value_rad, rel=1e-9) == 1.0

def test_arithmetic_type_errors():
    a = Angle.from_gon(50)
    with pytest.raises(TypeError):
        _ = a + 5
    with pytest.raises(TypeError):
        _ = a - "string"
    with pytest.raises(TypeError):
        _ = a / Angle.from_rad(1.0)

@pytest.mark.parametrize("rad, expected", [
    ( 1.0, 1.0),
    (-1.0, 1.0),
    ( 3*math.pi, 3*math.pi),   # Betrag vor Normalisierung
    (-3*math.pi, 3*math.pi),
])
def test_abs_without_normalise(rad, expected):
    """
    abs() soll den ungeklärten Betrag liefern,
    also abs(value_rad), ohne automatisch zu normieren.
    """
    a = Angle.from_rad(rad)
    b = abs(a)
    assert pytest.approx(b.value_rad, rel=1e-9) == expected

def test_abs_and_normalise_chain():
    """
    Wenn man danach normalisiert, verhält es sich erwartbar:
    """
    a = Angle.from_rad(-1.0)
    b = abs(a)
    b.normalise()
    # -1rad → Betrag 1rad → normalize bleibt 1rad
    assert pytest.approx(b.value_rad, rel=1e-9) == 1.0

def test_abs_type_error():
    """
    abs() auf Nicht-Angle-Objekt ist nicht relevant – Python ruft nur __abs__ auf Angle-Instanzen.
    """
    with pytest.raises(TypeError):
        # falls jemand fälschlich versucht, abs mit einem anderen Typ zu tricksen
        _ = Angle.from_rad(1.0).__abs__("invalid")