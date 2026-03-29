import json, uuid, os

"""
from datetime import datetime
from app.repository.interfaces.log_repository_interface import ILogRepository
from app.model.log_entry import LogEntry

# Resolve data path to package root, not CWD
_PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(_PACKAGE_ROOT, "data")
LOGS_PATH = os.path.join(DATA_DIR, "logs.json")

class LogRepository(ILogRepository):
    def __init__(self, path=LOGS_PATH):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump({"eventos": []}, f, ensure_ascii=False, indent=2)

    def add(self, entry: LogEntry) -> None:
        if not isinstance(entry, LogEntry):
            raise TypeError("LogRepository.add expects a LogEntry object")
        
        with open(self.path, "r", encoding="utf-8") as f:
            db = json.load(f)

        if "eventos" not in db:
            db["eventos"] = []

        db["eventos"].append(entry.to_dict())

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2)

    def get_all(self):
        with open(self.path, "r", encoding="utf-8") as f:
            db = json.load(f)
        return db.get("eventos", [])

"""

from app.model.reading import Reading
from app.repository.interfaces.reading_repository_interface import IReadingRepository


class ReadingRepository(IReadingRepository):
    def __init__(self, db):
        self.db = db

    def add_reading(self, reading: Reading) -> None:
        """
        En la tabla readings el orden sería:
        [
            from_sensor_id,
            value,
            unit
        ]
        timestamp se genera solo en la BD
        """

        data = [
            reading.sensor_id,
            reading.value,
            reading.unit
        ]

        self.db.add("readings", data)

    def find_by_sensor(self, sensor_id: int):
        response = self.db.select("readings", "from_sensor_id", sensor_id)

        readings = []
        for row in response:
            reading = Reading(
                row[0],  # reading_id
                row[1],  # from_sensor_id
                row[2],  # value
                row[3],  # unit
                row[4]   # timestamp
            )
            readings.append(reading)

        return readings

    def get_all(self):
        response = self.db.select_all("readings")

        readings = []
        for row in response:
            reading = Reading(
                row[0],  # reading_id
                row[1],  # from_sensor_id
                row[2],  # value
                row[3],  # unit
                row[4]   # timestamp
            )
            readings.append(reading)

        return readings

    def save(self) -> None:
        pass