from __future__ import annotations
from dataclasses import dataclass, asdict
from uuid import UUID, uuid4
from datetime import datetime, timezone
from .enums import ActuatorTypeEnum


@dataclass(slots=True)
class Actuator:
    id: UUID
    name: str
    type: str
    location: str
    community_id: int
    state: bool = False
    created_at: datetime = datetime.now(timezone.utc)
    lastChangedAt: datetime = datetime.now(timezone.utc)
    # Automation-related fields can be added here in the future
    # Sensor-bindings can also be added here in the future

    @staticmethod
    def new(name: str, type: str, community_id: int, state: bool = False, created_at: datetime = datetime.now(timezone.utc) ) -> "Actuator":
        return Actuator(
            id=uuid4(),
            community_id=community_id,
            name=name,
            type=type,
            state=state,
            created_at=created_at,
            lastChangedAt=datetime.now(timezone.utc),

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

    def to_row(self):
        return [
            str(self.id),
            self.name,
            self.type,
            self.state,
            self.lastChangedAt.isoformat()
        ]