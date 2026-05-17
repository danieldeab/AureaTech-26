from __future__ import annotations

from typing import Optional

from app.model.enums import RoleEnum
from app.model.log_entry import LogEntry
from app.repository.log_repository import LogRepository


class AuditLogService:
    def __init__(self, log_repository: LogRepository | None = None):
        self.log_repository = log_repository or LogRepository()

    def log(
        self,
        *,
        actor_id: int,
        actor_role: RoleEnum,
        category: str,
        action: str,
        details: str = "",
        community_id: Optional[int] = None,
        target_entity_type: Optional[str] = None,
        target_entity_id: Optional[int] = None,
    ) -> None:
        entry = LogEntry.new(
            actor_id=actor_id,
            actor_role=actor_role,
            category=category,
            action=action,
            details=details,
            community_id=community_id,
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
        )
        self.log_repository.add(entry)
