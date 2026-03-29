from __future__ import annotations

from typing import List, Optional

from app.infraestructure.db import get_db
from app.model.sensor import Sensor
from app.repository.interfaces.sensor_repository_interface import ISensorRepository


class SensorRepository(ISensorRepository):
    """
    MariaDB-backed repository for Sensor.

    Source of truth:
    - table: sensor
    - columns:
        sensor_id, community_id, sensor_type, location, is_enabled, created_at
    """

    def __init__(self):
        self.db = get_db()

    # --------------------------------------------------
    # Mapping helpers
    # --------------------------------------------------
    def _row_to_sensor(self, row: dict) -> Sensor:
        return Sensor(
            sensor_id=row["sensor_id"],
            from_community_id=row["community_id"],
            type=row["sensor_type"],
            location=row["location"],
            is_enabled=bool(row["is_enabled"]),
            created_at=row["created_at"],
        )

    def _sensor_to_db_data(self, sensor: Sensor) -> dict:
        return {
            "community_id": sensor.from_community_id,
            "sensor_type": sensor.type,
            "location": sensor.location,
            "is_enabled": int(bool(sensor.is_enabled)),
        }

    # --------------------------------------------------
    # Interface API
    # --------------------------------------------------
    def add_sensor(self, sensor: Sensor) -> None:
        new_id = self.db.insert(
            table="sensor",
            data=self._sensor_to_db_data(sensor),
        )
        sensor.sensor_id = new_id

    def find_by_id(self, sensor_id: str | int) -> Optional[Sensor]:
        row = self.db.fetch_one(
            table="sensor",
            where={"sensor_id": int(sensor_id)},
        )
        return self._row_to_sensor(row) if row else None

    def get_all(self) -> List[Sensor]:
        rows = self.db.fetch_all(
            table="sensor",
            order_by="sensor_id ASC",
        )
        return [self._row_to_sensor(row) for row in rows]

    def save(self, sensor: Sensor) -> None:
        if sensor.sensor_id is None:
            self.add_sensor(sensor)
            return

        self.db.update(
            table="sensor",
            data=self._sensor_to_db_data(sensor),
            where={"sensor_id": sensor.sensor_id},
        )

    # --------------------------------------------------
    # Legacy compatibility API
    # --------------------------------------------------
    def findAll(self) -> List[Sensor]:
        return self.get_all()

    def findById(self, sensor_id: str | int) -> Optional[Sensor]:
        return self.find_by_id(sensor_id)