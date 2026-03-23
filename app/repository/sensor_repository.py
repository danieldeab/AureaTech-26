import json
import os
from typing import List
from uuid import uuid4, UUID

from app.repository.interfaces.sensor_repository_interface import ISensorRepository
from app.model.sensor import Sensor

# Resolve to package root data directory regardless of CWD
_PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(_PACKAGE_ROOT, "data")
SENSORS_PATH = os.path.join(DATA_DIR, "sensores.json")

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

        # Admitimos tanto lista simple como objeto con clave "sensores"
        if isinstance(data, dict) and "sensores" in data:
            data = data["sensores"]
        if not isinstance(data, list):
            data = []

        loaded: List[Sensor] = []
        for s in data:
            try:
                loaded.append(Sensor.from_dict(s))
            except Exception as e:
                print(f"[SensorRepository] Error loading sensor: {e}\nData: {s}")
        return loaded

    def add_sensor(self, sensor: Sensor) -> None:
        # Simplemente añadimos la entidad; la factoría del modelo ya genera el id
        # Ensure it has an id
        if getattr(sensor, "id", None) is None:
            sensor.id = uuid4()
        self.sensors.append(sensor)

    def find_by_id(self, sensor_id: str):
        # Permite buscar con str o UUID
        for s in self.sensors:
            sid = str(s.id) if isinstance(s.id, (UUID,)) else s.id
            if sid == str(sensor_id):
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
