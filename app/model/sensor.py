from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict
from uuid import UUID, uuid4

@dataclass(slots=True)
class Sensor:
    id: UUID
    type: str
    location: str
    thresholds: Dict[str, float] = field(default_factory=dict)

    @staticmethod
    def new(type: str, location: str, thresholds: Dict[str, float] | None = None) -> "Sensor":
        return Sensor(id=uuid4(), type=type, location=location, thresholds=thresholds or {})

    def to_dict(self) -> dict:
        d = asdict(self)
        d["id"] = str(self.id)
        return d

    @staticmethod
    def from_dict(d: dict) -> "Sensor":
        return Sensor(id=UUID(d["id"]), type=d["type"], location=d["location"], thresholds=d.get("thresholds", {}))
