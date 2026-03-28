from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timezone


@dataclass(slots=True)
class Sensor:
    type: str
    location: str
    from_community_id: int
    is_enabled: bool = False
    created_at: Optional[datetime] = None
    sensor_id: Optional[int] = None

    @staticmethod
    def new(
        from_community_id: int,
        type: str,
        location: str,
        is_enabled: bool = False,
    ) -> "Sensor":
        return Sensor(
            type=type,
            location=location,
            from_community_id=from_community_id,
            is_enabled=is_enabled,
        )

    def to_row(self) -> tuple:
        return (
            self.from_community_id,
            self.type,
            self.location,
            int(self.is_enabled),
        )

    def to_dict(self) -> dict:
        return {
            "sensor_id": self.sensor_id,
            "type": self.type,
            "location": self.location,
            "from_community_id": self.from_community_id,
            "is_enabled": self.is_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @staticmethod
    def from_dict(d: dict) -> "Sensor":
        return Sensor(
            sensor_id=d.get("sensor_id"),
            type=d["type"],
            location=d["location"],
            from_community_id=d["from_community_id"],
            is_enabled=bool(d.get("is_enabled", False)),
            created_at=datetime.fromisoformat(d["created_at"]) if d.get("created_at") else None,
        )