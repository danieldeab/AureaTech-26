import json
import os
from uuid import UUID

from app.repository.interfaces.sensor_repository_interface import ISensorRepository
from app.model.sensor import Sensor

# Resolve to package root data directory regardless of CWD
_PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(_PACKAGE_ROOT, "data")
SENSORS_PATH = os.path.join(DATA_DIR, "sensores.json")


class SensorRepository(ISensorRepository):
    def __init__(self, path=SENSORS_PATH):
        self.path = path
        self.sensors = self._load()

    def _load(self):
        if not os.path.exists(self.path):
            return []

        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Admitimos tanto lista simple como objeto con clave "sensores"
        if isinstance(data, dict) and "sensores" in data:
            data = data["sensores"]
        if not isinstance(data, list):
            data = []

        return [Sensor.from_dict(s) for s in data]

    def add_sensor(self, sensor: Sensor):
        # Simplemente añadimos la entidad; la factoría del modelo ya genera el id
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

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([s.to_dict() for s in self.sensors], f, ensure_ascii=False, indent=4)
