from __future__ import annotations
from dataclasses import dataclass, asdict
from uuid import UUID, uuid4
from datetime import datetime

@dataclass(slots=True)
class Actuator:
    id: UUID
    type: str
    state: bool
    last_changed_at: datetime

    @staticmethod
    def new(type: str, state: bool = False) -> "Actuator":
        from datetime import datetime
        return Actuator(id=uuid4(), type=type, state=state, last_changed_at=datetime.utcnow())

    def set_state(self, new_state: bool):
        if self.state != new_state:
            self.state = new_state
            from datetime import datetime
            self.last_changed_at = datetime.utcnow()

    def to_dict(self) -> dict:
        d = asdict(self)
        d["id"] = str(self.id)
        d["last_changed_at"] = self.last_changed_at.isoformat()
        return d

    @staticmethod
    def from_dict(d: dict) -> "Actuator":
        from datetime import datetime
        return Actuator(
            id=UUID(d["id"]),
            type=d["type"],
            state=bool(d["state"]),
            last_changed_at=datetime.fromisoformat(d["last_changed_at"]),
        )
