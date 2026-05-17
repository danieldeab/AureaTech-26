from __future__ import annotations
from dataclasses import dataclass, asdict
from uuid import UUID, uuid4
from datetime import datetime, timezone
from .enums import RoleEnum


@dataclass(slots=True)
class LogEntry:
    id: UUID
    timestamp: datetime
    actor_id: int
    actor_role: RoleEnum
    category: str
    action: str
    details: str
    community_id: int | None = None
    target_entity_type: str | None = None
    target_entity_id: int | None = None

    @staticmethod
    def new(
        actor_id: int,
        actor_role: RoleEnum,
        category: str,
        action: str,
        details: str = "",
        community_id: int | None = None,
        target_entity_type: str | None = None,
        target_entity_id: int | None = None,
    ) -> "LogEntry":
        return LogEntry(
            id=uuid4(),
            timestamp=datetime.now(timezone.utc),
            actor_id=int(actor_id),
            actor_role=actor_role,
            category=category,
            action=action,
            details=details,
            community_id=community_id,
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
        )

    def to_dict(self) -> dict:
        d = asdict(self)
        d["id"] = str(self.id)
        d["timestamp"] = self.timestamp.isoformat()
        d["actor_role"] = self.actor_role.value
        return d

    @staticmethod
    def from_dict(d: dict) -> "LogEntry":
        return LogEntry(
            id=UUID(d["id"]),
            timestamp=datetime.fromisoformat(d["timestamp"]),
            actor_id=int(d["actor_id"]),
            actor_role=RoleEnum(d["actor_role"]),
            category=d["category"],
            action=d["action"],
            details=d.get("details", ""),
            community_id=d.get("community_id"),
            target_entity_type=d.get("target_entity_type"),
            target_entity_id=d.get("target_entity_id"),
        )
