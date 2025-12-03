from __future__ import annotations
from dataclasses import dataclass, asdict
from uuid import UUID, uuid4
from datetime import datetime

@dataclass(slots=True)
class Reading:
    id: UUID
    sensor_id: UUID
    timestamp: datetime
    value: float
    unit: str

    @staticmethod
    def new(sensor_id: UUID, value: float, unit: str, timestamp: datetime | None = None) -> "Reading":
        return Reading(id=uuid4(), sensor_id=sensor_id, timestamp=timestamp or datetime.utcnow(), value=value, unit=unit)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["id"] = str(self.id)
        d["sensor_id"] = str(self.sensor_id)
        d["timestamp"] = self.timestamp.isoformat()
        return d

    @staticmethod
    def from_dict(d: dict) -> "Reading":
        return Reading(
            id=UUID(d["id"]),
            sensor_id=UUID(d["sensor_id"]),
            timestamp=datetime.fromisoformat(d["timestamp"]),
            value=float(d["value"]),
            unit=d["unit"],
        )
