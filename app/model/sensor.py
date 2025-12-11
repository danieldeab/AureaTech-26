# app/model/sensor.py

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from uuid import UUID, uuid4
from typing import Dict, List
from datetime import datetime
from .enums import SensorTypeEnum
from .reading import Reading


@dataclass(slots=True)
class Sensor:
    id: UUID
    type: str                     # we allow string; enums are optional at call site
    location: str
    thresholds: Dict[str, float] = field(default_factory=dict)
    community_id: int = 0
    readings: List[Reading] = field(default_factory=list)

    @staticmethod
    def new(type: str, location: str, community_id: int, thresholds=None) -> "Sensor":
        return Sensor(
            id=uuid4(),
            type=type,
            location=location,
            thresholds=thresholds or {},
            community_id=community_id,
            readings=[],
        )

    def to_dict(self) -> dict:
        d = asdict(self)
        d["id"] = str(self.id)
        d["readings"] = [r.to_dict() for r in self.readings]
        return d

    @staticmethod
    def from_dict(d: dict) -> "Sensor":
        sensor = Sensor(
            id=UUID(d["id"]),
            type=d["type"],
            location=d["location"],
            thresholds=d.get("thresholds", {}),
            community_id=d.get("community_id", 0),
            readings=[],
        )

        for rd in d.get("readings", []):
            try:
                sensor.readings.append(Reading.from_dict(rd))
            except:
                pass

        return sensor