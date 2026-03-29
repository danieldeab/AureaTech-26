from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .enums import SeverityEnum


@dataclass(slots=True)
class AlertDelivery:
    """
    Read-model / projection for UI and service use.
    Combines Alert + UserAlert information.
    Not a direct table entity.
    """

    alert_id: int
    user_alert_id: int | None
    user_id: int | None
    community_id: int
    rule_alert_action_id: int
    alert_type: str
    severity: SeverityEnum
    message: str
    created_at: datetime
    read_status: bool = False
    read_at: Optional[datetime] = None