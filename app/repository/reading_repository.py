from __future__ import annotations

from typing import List
from uuid import UUID

from app.infraestructure.db import get_db
from app.model.reading import Reading
from app.repository.interfaces.reading_repository_interface import IReadingRepository


class ReadingRepository(IReadingRepository):
    """
    MariaDB-backed repository for Reading.

    Source of truth:
    - table: reading
    - columns:
        reading_id, sensor_id, reading_value, unit, recorded_at
    """

    def __init__(self):
        self.db = get_db()

    # --------------------------------------------------
    # Mapping helpers
    # --------------------------------------------------
    def _row_to_reading(self, row: dict) -> Reading:
        return Reading(
            id=row["reading_id"],
            sensor_id=row["sensor_id"],
            timestamp=row["recorded_at"],
            value=float(row["reading_value"]),
            unit=row["unit"],
        )

    def _reading_to_db_data(self, reading: Reading) -> dict:
        return {
            "sensor_id": reading.sensor_id,
            "reading_value": reading.value,
            "unit": reading.unit,
        }

    # --------------------------------------------------
    # Interface API
    # --------------------------------------------------
    def add_reading(self, reading: Reading) -> None:
        new_id = self.db.insert(
            table="reading",
            data=self._reading_to_db_data(reading),
        )
        reading.id = new_id

    def find_by_sensor(self, sensor_id: UUID | int | str) -> List[Reading]:
        rows = self.db.fetch_all(
            table="reading",
            where={"sensor_id": sensor_id},
            order_by="recorded_at DESC",
        )
        return [self._row_to_reading(row) for row in rows]

    def get_all(self) -> List[Reading]:
        rows = self.db.fetch_all(
            table="reading",
            order_by="recorded_at DESC",
        )
        return [self._row_to_reading(row) for row in rows]
