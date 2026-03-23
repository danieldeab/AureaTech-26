import json
import os
from typing import List
from uuid import UUID

from app.model.reading import Reading
from app.repository.interfaces.reading_repository_interface import IReadingRepository

# Resolve data path relative to package root, independent of CWD
_PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(_PACKAGE_ROOT, "data")
READINGS_PATH = os.path.join(DATA_DIR, "readings.json")


class ReadingRepository(IReadingRepository):
    def __init__(self, path: str = READINGS_PATH):
        self.path = path
        self.readings: List[Reading] = self._load()

    def _load(self) -> List[Reading]:
        # Asegura directorio y archivo si no existe
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            return []

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []

        if isinstance(data, dict) and "lecturas" in data:
            data = data["lecturas"]
        if not isinstance(data, list):
            data = []

        return [Reading.from_dict(d) for d in data]

    def add_reading(self, reading: Reading) -> None:
        self.readings.append(reading)

    def find_by_sensor(self, sensor_id: UUID) -> List[Reading]:
        sid = str(sensor_id)
        return [r for r in self.readings if str(r.sensor_id) == sid]

    def get_all(self) -> List[Reading]:
        return self.readings

    def save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([r.to_dict() for r in self.readings], f, ensure_ascii=False, indent=2)
