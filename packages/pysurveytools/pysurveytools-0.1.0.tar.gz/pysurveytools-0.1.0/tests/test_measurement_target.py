import pytest

from surveytools import MeasurementTarget, Measurement, Angle

# 1. Erstelle jeweils zwei Measurement-Instanzen für face1
m1_f1 = Measurement(
    target=1,
    direction=Angle.from_gon(172.1609),    # Horizontalwinkel in Gon
    zenith=Angle.from_gon(97.1722),        # Zenitwinkel in Gon
    sd=12.287,                          # Schrägentfernung
    atmospheric_data={"pressure": 1013.25},
    measure_time="2025-05-26T10:00:00"
)
m2_f1 = Measurement(
    target=1,
    direction=Angle.from_gon(172.1659),
    zenith=Angle.from_gon(97.1682),
    sd=12.29,
    atmospheric_data={"pressure": 1013.25},
    measure_time="2025-05-26T10:01:00"
)

# 2. Erstelle jeweils zwei Measurement-Instanzen für face2
m1_f2 = Measurement(
    target=1,
    direction=Angle.from_gon(372.1589),
    zenith=Angle.from_gon(302.8283),
    sd=12.292,
    atmospheric_data={"pressure": 1013.25},
    measure_time="2025-05-26T10:02:00"
)
m2_f2 = Measurement(
    target=1,
    direction=Angle.from_gon(372.1589),
    zenith=Angle.from_gon(302.8322),
    sd=12.285,
    atmospheric_data={"pressure": 1013.25},
    measure_time="2025-05-26T10:03:00"
)

# 3. Instanziiere das MeasurementTarget
target = MeasurementTarget(
    target=1,
    direction=Angle.from_gon(172),   # Referenzrichtung
    zenith=Angle.from_gon(97),       # Referenzzenit
    distance=12.3                    # Referenzentfernung
)  # face1 und face2 sind zunächst leere Listen

# 4. Fülle face1 und face2
target.face1.extend([m1_f1, m2_f1])
target.face2.extend([m1_f2, m2_f2])

# 5. Optional: Auswertung durchführen
result = target.evaluation(zero_direction=Angle.from_rad(0))


def test_measurement_target_evaluation_practical():
    # 4) Auswertung prüfen
    #    Direction: (172.1609 + 172.1659 + (372.1589-200)*2) / 4 ≈ 172.1612 gon
    assert result.direction.get_gon() == pytest.approx(172.1612, abs=1e-4)

    #    Zenith: (97.1722 + 97.1682 + (400-302.8283) + (400-302.8322)) / 4 ≈ 97.1700 gon
    assert result.zenith.get_gon() == pytest.approx(97.1700, abs=1e-4)

    #    Slope distance: (12.287 + 12.290 + 12.292 + 12.285) / 4 ≈ 12.2885
    assert result.slope_distances == pytest.approx(12.2885, abs=1e-4)
