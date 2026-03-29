from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional

from .enums import SeverityEnum

@dataclass(slots=True)
class Alert:
    """
    DB-faithful alert entity.

    Maps to table:
        alert(
            alert_id,
            community_id,
            rule_alert_action_id,
            alert_type,
            severity,
            message,
            created_at
        )
    """
    id: int | None
    community_id: int
    rule_alert_action_id: int
    alert_type: str
    severity: SeverityEnum
    message: str
    created_at: datetime | None = None

    @staticmethod
    def new(
        *,
        community_id: int,
        rule_alert_action_id: int,
        alert_type: str,
        severity: SeverityEnum,
        message: str,
        created_at: datetime | None = None,
    ) -> "Alert":
        return Alert(
            id=None,
            community_id=community_id,
            rule_alert_action_id=rule_alert_action_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            created_at=created_at or datetime.now(timezone.utc),
        )

    def to_dict(self) -> dict:
        d = asdict(self)
        d["severity"] = self.severity.value
        d["created_at"] = self.created_at.isoformat() if self.created_at else None
        return d

    @staticmethod
    def from_dict(data: dict) -> "Alert":
        raw_severity = data["severity"]
        severity = raw_severity if isinstance(raw_severity, SeverityEnum) else SeverityEnum(str(raw_severity))

        raw_created_at = data.get("created_at")
        created_at = (
            datetime.fromisoformat(raw_created_at)
            if isinstance(raw_created_at, str) and raw_created_at
            else raw_created_at
        )

        return Alert(
            id=data.get("id"),
            community_id=data["community_id"],
            rule_alert_action_id=data["rule_alert_action_id"],
            alert_type=data["alert_type"],
            severity=severity,
            message=data["message"],
            created_at=created_at,
        )
