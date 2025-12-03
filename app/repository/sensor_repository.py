import json
import os
from typing import List
from uuid import uuid4

from app.repository.interfaces.sensor_repository_interface import ISensorRepository
from app.model.sensor import Sensor

SENSORS_PATH = os.path.join("data", "sensores.json")

class SensorRepository(ISensorRepository):
    """
    JSON-backed repository for Sensor entities.

    - Loads from data/sensores.json if it exists.
    - Exposes add_sensor / find_by_id / get_all / save.
    """

    def __init__(self, path: str = SENSORS_PATH):
        self.path = path
        self.sensors: List[Sensor] = self._load()

    # --------------------------------------------------
    # Internal loading
    # --------------------------------------------------
    def _load(self) -> List[Sensor]:
        if not os.path.exists(self.path):
            return []

        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Allow both {"sensores": [...]} and plain list [...]
        if isinstance(data, dict) and "sensores" in data:
            data = data["sensores"]

        loaded: List[Sensor] = []
        for s in data:
            try:
                loaded.append(Sensor.from_dict(s))
            except Exception as e:
                print(f"[SensorRepository] Error loading sensor: {e}\nData: {s}")
        return loaded

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------
    def add_sensor(self, sensor: Sensor) -> None:
        # Ensure it has an id
        if getattr(sensor, "id", None) is None:
            sensor.id = uuid4()
        self.sensors.append(sensor)

    def find_by_id(self, sensor_id: str):
        for s in self.sensors:
            if str(s.id) == str(sensor_id):
                return s
        return None

    def get_all(self):
        return self.sensors

    def save(self) -> None:
        """
        Persist all sensors to JSON in an atomic way to avoid file corruption.
        """
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        tmp_path = self.path + ".tmp"

        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(
                [s.to_dict() for s in self.sensors],
                f,
                ensure_ascii=False,
                indent=4,
            )

        os.replace(tmp_path, self.path)
