from __future__ import annotations

from datetime import datetime
from typing import Any

from app.infraestructure.db import get_db


class ErrorRepository:
    def __init__(self):
        self.db = get_db()

    def add(self, event: dict[str, Any]) -> int:
        return self.db.insert(
            table="error_event",
            data={
                "exception_type": event["exception_type"],
                "severity": event["severity"],
                "message": event["message"],
                "source_layer": event["source_layer"],
                "stacktrace": event.get("stacktrace"),
                "user_id": event.get("user_id"),
                "community_id": event.get("community_id"),
                "target_entity_type": event.get("target_entity_type"),
                "target_entity_id": event.get("target_entity_id"),
            },
        )

    def search(
        self,
        filters: dict[str, Any] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        filters = filters or {}
        where_clauses = ["1=1"]
        params: list[Any] = []

        if filters.get("start_date"):
            where_clauses.append("created_at >= %s")
            params.append(filters["start_date"])
        if filters.get("end_date"):
            where_clauses.append("created_at <= %s")
            params.append(filters["end_date"])
        if filters.get("severity"):
            where_clauses.append("severity = %s")
            params.append(filters["severity"])
        if filters.get("source_layer"):
            where_clauses.append("source_layer = %s")
            params.append(filters["source_layer"])
        if filters.get("exception_type"):
            where_clauses.append("exception_type = %s")
            params.append(filters["exception_type"])
        if filters.get("community_id") is not None:
            where_clauses.append("community_id = %s")
            params.append(filters["community_id"])
        if filters.get("user_id") is not None:
            where_clauses.append("user_id = %s")
            params.append(filters["user_id"])

        sql = """
            SELECT
                error_id,
                exception_type,
                severity,
                message,
                source_layer,
                stacktrace,
                user_id,
                community_id,
                target_entity_type,
                target_entity_id,
                created_at
            FROM error_event
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
        out: list[dict[str, Any]] = []
        for row in rows:
            created_at = row.get("created_at")
            out.append(
                {
                    "id": str(row["error_id"]),
                    "timestamp": created_at.isoformat() if isinstance(created_at, datetime) else "",
                    "exception_type": row.get("exception_type"),
                    "severity": row.get("severity"),
                    "message": row.get("message"),
                    "source_layer": row.get("source_layer"),
                    "stacktrace": row.get("stacktrace"),
                    "user_id": row.get("user_id"),
                    "community_id": row.get("community_id"),
                    "target_entity_type": row.get("target_entity_type"),
                    "target_entity_id": row.get("target_entity_id"),
                }
            )
        return out
