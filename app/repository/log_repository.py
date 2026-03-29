from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Any

from app.infraestructure.db import get_db
from app.model.log_entry import LogEntry
from app.repository.interfaces.log_repository_interface import ILogRepository


class LogRepository(ILogRepository):
    """
    MariaDB-backed repository for audit logs.

    DB source of truth:
    - table: audit_log
    - columns:
        log_id, user_id, actor_role, category, action, details, created_at

    Read API intentionally returns legacy dicts because DashboardService
    still expects the old JSON-style shape.
    """

    def __init__(self):
        self.db = get_db()

    # --------------------------------------------------
    # Write path
    # --------------------------------------------------
    def add(self, entry: Dict | LogEntry):
        """
        Accepts either:
        - LogEntry dataclass
        - legacy dict-like entry
        """
        if isinstance(entry, LogEntry):
            actor_id = entry.actor_id
            actor_role = entry.actor_role.value if hasattr(entry.actor_role, "value") else str(entry.actor_role)
            category = entry.category
            action = entry.action
            details = entry.details or ""

            # audit_log.user_id is INT NOT NULL in the schema
            # If actor_id is not coercible to int, fail loudly rather than corrupting data.
            try:
                user_id = int(actor_id)
            except Exception as exc:
                raise ValueError(
                    f"audit_log.user_id must be an int-compatible value, got {actor_id!r}"
                ) from exc

            self.db.insert(
                table="audit_log",
                data={
                    "user_id": user_id,
                    "actor_role": actor_role,
                    "category": category,
                    "action": action,
                    "details": details,
                },
            )
            return

        if isinstance(entry, dict):
            raw_user_id = entry.get("user_id")
            try:
                user_id = int(raw_user_id)
            except Exception as exc:
                raise ValueError(
                    f"legacy log dict must include an int-compatible user_id, got {raw_user_id!r}"
                ) from exc

            metadata = entry.get("metadata", {}) or {}
            self.db.insert(
                table="audit_log",
                data={
                    "user_id": user_id,
                    "actor_role": str(metadata.get("actor_role", "SYSTEM")),
                    "category": str(metadata.get("category", "GENERAL")),
                    "action": str(entry.get("event_type", "unknown")),
                    "details": str(entry.get("description", "")),
                },
            )
            return

        raise TypeError("LogRepository.add expects LogEntry or dict")

    # --------------------------------------------------
    # Read path
    # --------------------------------------------------
    def all(self) -> List[Dict[str, Any]]:
        rows = self.db.fetch_all(
            table="audit_log",
            order_by="created_at DESC",
        )

        results: List[Dict[str, Any]] = []
        for row in rows:
            created_at = row["created_at"]

            if isinstance(created_at, datetime):
                ts = int(created_at.replace(tzinfo=timezone.utc).timestamp())
            else:
                # defensive fallback
                ts = 0

            results.append(
                {
                    "id": str(row["log_id"]),
                    "ts": ts,
                    "event_type": row["action"],
                    "user_id": str(row["user_id"]) if row["user_id"] is not None else None,
                    "description": row["details"] or "",
                    "metadata": {
                        "category": row["category"],
                        "actor_role": row["actor_role"],
                    },
                }
            )

        return results