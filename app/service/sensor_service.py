from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.model.sensor import Sensor
from app.model.reading import Reading
from app.repository.sensor_repository import SensorRepository
from app.repository.reading_repository import ReadingRepository


class SensorService:
    """
    Application service for sensor-related operations.
    Relational version: readings are queried from ReadingRepository,
    not embedded inside Sensor objects.
    """

    def __init__(self, sensor_repo: SensorRepository, reading_repo: ReadingRepository):
        self.sensor_repo = sensor_repo
        self.reading_repo = reading_repo

    def get_sensors_in_community(self, community_id: int) -> List[Sensor]:
        sensors = self.sensor_repo.get_all()
        return [s for s in sensors if s.from_community_id == community_id]

    def get_sensor(self, sensor_id: str | int | UUID) -> Optional[Sensor]:
        if hasattr(self.sensor_repo, "find_by_id"):
            return self.sensor_repo.find_by_id(sensor_id)
        return self.sensor_repo.findById(str(sensor_id))

    def get_readings(
        self,
        *,
        sensor_id: Optional[str | int | UUID] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 500,
    ) -> List[Reading]:

        if sensor_id is not None:
            readings = self.reading_repo.find_by_sensor(sensor_id)
        else:
            readings = self.reading_repo.get_all()

        filtered: List[Reading] = []
        for r in readings:
            if start and r.timestamp < start:
                continue
            if end and r.timestamp > end:
                continue
            filtered.append(r)

        filtered.sort(key=lambda r: r.timestamp, reverse=True)
        return filtered[:limit]