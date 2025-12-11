# app/service/sensor_service.py

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
    No simulation here — simulation is handled by generator utils.
    """

    def __init__(self, sensor_repo: SensorRepository, reading_repo: ReadingRepository):
        self.sensor_repo = sensor_repo
        self.reading_repo = reading_repo

    # -----------------------------------------------------------
    # SENSOR QUERIES
    # -----------------------------------------------------------

    def get_sensors_in_community(self, community_id: int) -> List[Sensor]:
        sensors = self.sensor_repo.findAll()
        return [s for s in sensors if s.community_id == community_id]

    def get_sensor(self, sensor_id: str | UUID) -> Optional[Sensor]:
        return self.sensor_repo.findById(str(sensor_id))

    # -----------------------------------------------------------
    # READING QUERIES
    # -----------------------------------------------------------

    def get_readings(
        self,
        *,
        sensor_id: Optional[str | UUID] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 500,
    ) -> List[Reading]:

        if sensor_id:
            sensor = self.sensor_repo.findById(str(sensor_id))
            if not sensor:
                return []
            readings = sensor.readings
        else:
            readings = []
            for s in self.sensor_repo.findAll():
                readings.extend(s.readings)

        # Apply filters
        filtered = []
        for r in readings:
            if start and r.timestamp < start:
                continue
            if end and r.timestamp > end:
                continue
            filtered.append(r)

        filtered.sort(key=lambda r: r.timestamp, reverse=True)
        return filtered[:limit]
