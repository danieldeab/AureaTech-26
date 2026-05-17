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
                    "community_id": getattr(entry, "community_id", None),
                    "target_entity_type": getattr(entry, "target_entity_type", None),
                    "target_entity_id": getattr(entry, "target_entity_id", None),
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
                    "community_id": metadata.get("community_id"),
                    "target_entity_type": metadata.get("target_entity_type"),
                    "target_entity_id": metadata.get("target_entity_id"),
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
                    "community_id": row.get("community_id"),
                    "description": row["details"] or "",
                    "metadata": {
                        "category": row["category"],
                        "actor_role": row["actor_role"],
                        "target_entity_type": row.get("target_entity_type"),
                        "target_entity_id": row.get("target_entity_id"),
                    },
                }
            )

        return results

    def search(
        self,
        filters: Dict[str, Any] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> List[Dict[str, Any]]:
        filters = filters or {}

        where_clauses = ["1=1"]
        params: list[Any] = []

        if filters.get("start_date"):
            where_clauses.append("created_at >= %s")
            params.append(filters["start_date"])
        if filters.get("end_date"):
            where_clauses.append("created_at <= %s")
            params.append(filters["end_date"])
        if filters.get("category"):
            where_clauses.append("category = %s")
            params.append(filters["category"])
        if filters.get("actor_role"):
            where_clauses.append("actor_role = %s")
            params.append(filters["actor_role"])
        if filters.get("action"):
            where_clauses.append("action = %s")
            params.append(filters["action"])
        if filters.get("event_type"):
            where_clauses.append("action = %s")
            params.append(filters["event_type"])
        if filters.get("user_id"):
            where_clauses.append("user_id = %s")
            params.append(filters["user_id"])
        if filters.get("community_id") is not None:
            where_clauses.append("community_id = %s")
            params.append(filters["community_id"])
        if filters.get("target_entity_type"):
            where_clauses.append("target_entity_type = %s")
            params.append(filters["target_entity_type"])
        if filters.get("target_entity_id") is not None:
            where_clauses.append("target_entity_id = %s")
            params.append(filters["target_entity_id"])

        sql = """
            SELECT
                log_id,
                user_id,
                actor_role,
                category,
                action,
                details,
                community_id,
                target_entity_type,
                target_entity_id,
                created_at
            FROM audit_log
            WHERE {where_sql}
            ORDER BY created_at DESC
        """.format(where_sql=" AND ".join(where_clauses))

        if limit is not None:
            sql += " LIMIT %s"
            params.append(int(limit))
            if offset is not None:
                sql += " OFFSET %s"
                params.append(int(offset))

        rows = self.db.execute(sql, tuple(params))
        results: List[Dict[str, Any]] = []
        for row in rows:
            created_at = row["created_at"]
            ts = int(created_at.replace(tzinfo=timezone.utc).timestamp()) if isinstance(created_at, datetime) else 0
            results.append(
                {
                    "id": str(row["log_id"]),
                    "ts": ts,
                    "event_type": row["action"],
                    "user_id": str(row["user_id"]) if row["user_id"] is not None else None,
                    "community_id": row.get("community_id"),
                    "description": row.get("details") or "",
                    "metadata": {
                        "category": row.get("category"),
                        "actor_role": row.get("actor_role"),
                        "target_entity_type": row.get("target_entity_type"),
                        "target_entity_id": row.get("target_entity_id"),
                    },
                }
            )
        return results
