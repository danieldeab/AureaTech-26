from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class UserAlert:
    """
    DB-faithful user-alert delivery entity.

    Maps to table:
        user_alert(
            user_alert_id,
            user_id,
            alert_id,
            read_status,
            read_at
        )
    """

    id: int | None
    user_id: int
    alert_id: int
    read_status: bool = False
    read_at: Optional[datetime] = None

    @staticmethod
    def new(
        *,
        user_id: int,
        alert_id: int,
        read_status: bool = False,
        read_at: Optional[datetime] = None,
    ) -> "UserAlert":
        return UserAlert(
            id=None,
            user_id=user_id,
            alert_id=alert_id,
            read_status=read_status,
            read_at=read_at,
        )

    def mark_read(self, when: Optional[datetime] = None) -> None:
        self.read_status = True
        self.read_at = when or datetime.now()

    def to_dict(self) -> dict:
        d = asdict(self)
        d["read_at"] = self.read_at.isoformat() if self.read_at else None
        return d

    @staticmethod
    def from_dict(data: dict) -> "UserAlert":
        raw_read_at = data.get("read_at")
        read_at = (
            datetime.fromisoformat(raw_read_at)
            if isinstance(raw_read_at, str) and raw_read_at
            else raw_read_at
        )

        return UserAlert(
            id=data.get("id"),
            user_id=data["user_id"],
            alert_id=data["alert_id"],
            read_status=bool(data.get("read_status", False)),
            read_at=read_at,
        )