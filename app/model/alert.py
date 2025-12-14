from __future__ import annotations
from dataclasses import dataclass, asdict
from uuid import UUID, uuid4
from datetime import datetime, timezone
from .enums import SeverityEnum

@dataclass(slots=True)
class Alert:
    id: UUID
    type: str
    severity: SeverityEnum
    message: str
    target_user_id: UUID
    timestamp: datetime
    read_status: bool = False

    @staticmethod
    def new(type: str, severity: SeverityEnum, message: str, target_user_id: UUID) -> "Alert":
        return Alert(
            id=uuid4(),
            type=type,
            severity=severity,
            message=message,
            target_user_id=target_user_id,
            timestamp=datetime.now(timezone.utc),
            read_status=False,
        )

    def to_dict(self) -> dict:
        d = asdict(self)
        d["id"] = str(self.id)
        d["target_user_id"] = str(self.target_user_id)
        d["severity"] = self.severity.value
        d["timestamp"] = self.timestamp.isoformat()
        return d

    @staticmethod
    def from_dict(d: dict) -> "Alert":
        from datetime import datetime, timezone
        return Alert(
            id=UUID(d["id"]),
            type=d["type"],
            severity=SeverityEnum(d["severity"]),
            message=d["message"],
            target_user_id=UUID(d["target_user_id"]),
            timestamp=datetime.fromisoformat(d["timestamp"]),
            read_status=bool(d.get("read_status", False)),
        )
