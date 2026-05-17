from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from app.model.reading import Reading


DEFAULT_SENSOR_UNITS: dict[str, str] = {
    "TEMPERATURE": "C",
    "HUMIDITY": "%",
    "LIGHT": "lux",
    "DISTANCE": "cm",
    "SMOKE": "ppm",
    "WIND": "km/h",
}


class ReadingService:
    def __init__(self, sensor_repo, reading_repo, monitoring_service):
        self.sensor_repo = sensor_repo
        self.reading_repo = reading_repo
        self.monitoring_service = monitoring_service

    def _coerce_float(self, raw_value: Any) -> float:
        try:
            return float(raw_value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid reading value: {raw_value!r}") from exc

    def record_reading(
        self,
        *,
        sensor_id: int,
        value: Any,
        unit: Optional[str] = None,
        recorded_at: Optional[datetime | str] = None,
        raw_payload: Optional[dict] = None,
        recipient_user_ids: Optional[list[int]] = None,
        user_id: Optional[int] = None,
    ) -> Reading:
        sensor = self.sensor_repo.find_by_id(sensor_id)
        if not sensor:
            raise ValueError(f"Sensor {sensor_id} not found.")
        if not bool(getattr(sensor, "is_enabled", False)):
            raise ValueError(f"Sensor {sensor_id} is disabled.")

        sensor_type = str(sensor.type).upper()
        normalized_value = self._coerce_float(value)
        normalized_unit = unit or DEFAULT_SENSOR_UNITS.get(sensor_type, "")
        normalized_timestamp = self._normalize_timestamp(recorded_at)

        reading = Reading(
            id=None,  # type: ignore[arg-type]
            sensor_id=int(sensor_id),  # type: ignore[arg-type]
            timestamp=normalized_timestamp,
            value=normalized_value,
            unit=normalized_unit,
        )
        self.reading_repo.add_reading(reading)

        self.monitoring_service.evaluate_reading_alerts(
            reading,
            sensor_type=sensor_type,
            community_id=int(sensor.from_community_id),
            recipient_user_ids=recipient_user_ids,
            user_id=user_id,
        )
        return reading

    def _normalize_timestamp(self, recorded_at: Optional[datetime | str]) -> datetime:
        if isinstance(recorded_at, datetime):
            return recorded_at
        if isinstance(recorded_at, str) and recorded_at.strip():
            return datetime.fromisoformat(recorded_at)
        return datetime.now(timezone.utc)
