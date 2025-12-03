import json
import os
import uuid
from datetime import datetime

from app.repository.interfaces.sensor_repository_interface import ISensorRepository
from app.model.sensor import Sensor

SENSORS_PATH = os.path.join("data", "sensores.json")


class SensorRepository(ISensorRepository):
    def __init__(self, path=SENSORS_PATH):
        self.path = path
        self.sensors = self._load()


    def _load(self):
        if not os.path.exists(self.path):
            return []

        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict) and "sensores" in data:
            data = data["sensores"]

        cleaned = []
        for s in data:
            cleaned.append(Sensor(**s))

        return cleaned

    def add_sensor(self, sensor: Sensor):
        # Create ID automatically if missing
        if not getattr(sensor, "id", None):
            sensor.id = str(uuid.uuid4())

        # Update last modified timestamp
        sensor.ultima_actualizacion = datetime.now().isoformat()
        self.sensors.append(sensor)

    def find_by_id(self, sensor_id: str):
        for s in self.sensors:
            if s.id == sensor_id:
                return s
        return None


    def get_all(self):
        return self.sensors


    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(
                [s.__dict__ for s in self.sensors],
                f,
                ensure_ascii=False,
                indent=4,
            )
