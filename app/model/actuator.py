# app/model/actuator.py

from __future__ import annotations
from dataclasses import dataclass, asdict
from uuid import UUID, uuid4
from datetime import datetime, timezone
from .enums import ActuatorTypeEnum


@dataclass(slots=True)
class Actuator:
    id: UUID
    name: str
    type: str                     # accept raw string or enum
    state: bool
    lastChangedAt: datetime
    community_id: int
    # Automation-related fields can be added here in the future
    # Sensor-bindings can also be added here in the future

    @staticmethod
    def new(name: str, type: str, community_id: int, state: bool = False) -> "Actuator":
        return Actuator(
            id=uuid4(),
            name=name,
            type=type,
            state=state,
            lastChangedAt=datetime.now(timezone.utc),
            community_id=community_id
        )

    def toggle(self):
        self.state = not self.state
        self.lastChangedAt = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["id"] = str(self.id)
        d["lastChangedAt"] = self.lastChangedAt.isoformat()
        return d

    @staticmethod
    def from_dict(d: dict) -> "Actuator":
        return Actuator(
            id=UUID(d["id"]),
            name=d["name"],
            type=d["type"],
            state=bool(d["state"]),
            lastChangedAt=datetime.fromisoformat(d["lastChangedAt"]),
            community_id=d.get("community_id", 0),
        )
