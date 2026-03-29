from __future__ import annotations
from dataclasses import dataclass, asdict
from uuid import UUID, uuid4
from datetime import datetime, timezone
from .enums import RoleEnum

@dataclass(slots=True)
class LogEntry:
    id: UUID
    timestamp: datetime
    actor_id: UUID
    actor_role: RoleEnum
    category: str       # 15 chars o menos (AUTH, AUTOMATION, ACTUATOR, DELETEUSER, MODPASSWD, )
    action: str
    details: str

    @staticmethod
    def new(actor_id: UUID, actor_role: RoleEnum, category: str, action: str, details: str = "") -> "LogEntry":
        return LogEntry(
            id=uuid4(),
            timestamp=datetime.now(timezone.utc),
            actor_id=actor_id,
            actor_role=actor_role,
            category=category,
            action=action,
            details=details,
        )

    def to_dict(self) -> dict:
        d = asdict(self)
        d["id"] = str(self.id)
        d["timestamp"] = self.timestamp.isoformat()
        d["actor_id"] = str(self.actor_id)
        d["actor_role"] = self.actor_role.value
        return d

    @staticmethod
    def from_dict(d: dict) -> "LogEntry":
        return LogEntry(
            id=UUID(d["id"]),
            timestamp=datetime.fromisoformat(d["timestamp"]),
            actor_id=UUID(d["actor_id"]),
            actor_role=RoleEnum(d["actor_role"]),
            category=d["category"],
            action=d["action"],
            details=d.get("details", ""),
        )
