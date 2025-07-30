from typing import List

from surveytools import MeasurementTarget, Measurement, Angle


class InstrumentStation:

    def __init__(self, station_name: str):
        self.station_name = station_name
        self.targets : dict[str, MeasurementTarget]  = dict()
        self.orientation : Angle = Angle.from_rad(0)

    def add_measurement_target(self, target : MeasurementTarget):
        self.targets[target.target_number] = target

    def evaluation(self) -> List[Measurement]:
        return [x.evaluation(self.orientation) for x in self.targets.values()]

