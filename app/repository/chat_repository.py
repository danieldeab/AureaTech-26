from __future__ import annotations

from datetime import datetime
from typing import List, Dict, Any, Optional

from app.infraestructure.db import get_db


class ChatRepository:
    """
    MariaDB-backed chat repository.

    DB source of truth:
    - chat_thread
    - chat_message

    Returns compatibility dicts expected by current controllers/views.
    """

    def __init__(self):
        self.db = get_db()

    def _row_to_thread_dict(self, row: dict) -> Dict[str, Any]:
        return {
            "id": row["thread_id"],
            "community_id": row["community_id"],
            "created_by_user_id": row["created_by_user_id"],
            "assigned_user_id": row["assigned_user_id"],
            "title": row["subject"],
            "status": row["status"],
            "created_at": row["created_at"],
            "resolved_at": row["closed_at"],
            "neighbor_id": row["created_by_user_id"],
            "technician_id": row["assigned_user_id"],
            "neighbor_name": row.get("neighbor_name", "Unknown neighbor"),
            "last_message_preview": row.get("last_message_preview"),
            "last_message_at": row.get("last_message_at"),
        }

    def _row_to_message_dict(self, row: dict) -> Dict[str, Any]:
        return {
            "id": row["message_id"],
            "chat_id": row["thread_id"],
            "sender_id": row["sender_user_id"],
            "sender_role": row["sender_role"],
            "sender_name": row.get("sender_name") or row["sender_role"],
            "text": row["content"],
            "timestamp": row["sent_at"],
        }

    def get_threads_for_technician(self, technician_id: int | str) -> List[Dict[str, Any]]:
        sql = """
            SELECT
                ct.thread_id,
                ct.community_id,
                ct.created_by_user_id,
                ct.assigned_user_id,
                ct.subject,
                ct.status,
                ct.created_at,
                ct.closed_at,
                u.full_name AS neighbor_name,
                (
                    SELECT cm.content
                    FROM chat_message cm
                    WHERE cm.thread_id = ct.thread_id
                    ORDER BY cm.sent_at DESC, cm.message_id DESC
                    LIMIT 1
                ) AS last_message_preview,
                (
                    SELECT cm.sent_at
                    FROM chat_message cm
                    WHERE cm.thread_id = ct.thread_id
                    ORDER BY cm.sent_at DESC, cm.message_id DESC
                    LIMIT 1
                ) AS last_message_at
            FROM chat_thread ct
            INNER JOIN user u
                ON u.user_id = ct.created_by_user_id
            INNER JOIN user tech
                ON tech.user_id = %s
            WHERE ct.assigned_user_id = %s
               OR (ct.assigned_user_id IS NULL AND ct.community_id = tech.community_id)
            ORDER BY COALESCE(ct.closed_at, ct.created_at) DESC, ct.thread_id DESC
        """
        rows = self.db.execute(sql, (int(technician_id), int(technician_id)))
        return [self._row_to_thread_dict(row) for row in rows]

    def get_threads_for_neighbor(self, neighbor_id: int | str) -> List[Dict[str, Any]]:
        return self.search_threads({"created_by_user_id": int(neighbor_id)})

    def search_threads(
        self,
        filters: dict[str, Any] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> List[Dict[str, Any]]:
        filters = filters or {}
        where_clauses = ["1=1"]
        params: list[Any] = []

        if filters.get("community_id") is not None:
            where_clauses.append("ct.community_id = %s")
            params.append(int(filters["community_id"]))
        if filters.get("assigned_user_id") is not None:
            where_clauses.append("ct.assigned_user_id = %s")
            params.append(int(filters["assigned_user_id"]))
        if filters.get("created_by_user_id") is not None:
            where_clauses.append("ct.created_by_user_id = %s")
            params.append(int(filters["created_by_user_id"]))
        if filters.get("status"):
            where_clauses.append("ct.status = %s")
            params.append(str(filters["status"]).upper())

        sql = """
            SELECT
                ct.thread_id,
                ct.community_id,
                ct.created_by_user_id,
                ct.assigned_user_id,
                ct.subject,
                ct.status,
                ct.created_at,
                ct.closed_at,
                u.full_name AS neighbor_name,
                (
                    SELECT cm.content
                    FROM chat_message cm
                    WHERE cm.thread_id = ct.thread_id
                    ORDER BY cm.sent_at DESC, cm.message_id DESC
                    LIMIT 1
                ) AS last_message_preview,
                (
                    SELECT cm.sent_at
                    FROM chat_message cm
                    WHERE cm.thread_id = ct.thread_id
                    ORDER BY cm.sent_at DESC, cm.message_id DESC
                    LIMIT 1
                ) AS last_message_at
            FROM chat_thread ct
            INNER JOIN user u
                ON u.user_id = ct.created_by_user_id
            WHERE {where_sql}
            ORDER BY COALESCE(ct.closed_at, ct.created_at) DESC, ct.thread_id DESC
        """.format(where_sql=" AND ".join(where_clauses))

        if limit is not None:
            sql += " LIMIT %s"
            params.append(int(limit))
            if offset is not None:
                sql += " OFFSET %s"
                params.append(int(offset))

        rows = self.db.execute(sql, tuple(params))
        return [self._row_to_thread_dict(row) for row in rows]

    def get_chat_by_id(self, chat_id: int | str) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT
                ct.thread_id,
                ct.community_id,
                ct.created_by_user_id,
                ct.assigned_user_id,
                ct.subject,
                ct.status,
                ct.created_at,
                ct.closed_at,
                u.full_name AS neighbor_name,
                (
                    SELECT cm.content
                    FROM chat_message cm
                    WHERE cm.thread_id = ct.thread_id
                    ORDER BY cm.sent_at DESC, cm.message_id DESC
                    LIMIT 1
                ) AS last_message_preview,
                (
                    SELECT cm.sent_at
                    FROM chat_message cm
                    WHERE cm.thread_id = ct.thread_id
                    ORDER BY cm.sent_at DESC, cm.message_id DESC
                    LIMIT 1
                ) AS last_message_at
            FROM chat_thread ct
            INNER JOIN user u
                ON u.user_id = ct.created_by_user_id
            WHERE ct.thread_id = %s
        """
        rows = self.db.execute(sql, (int(chat_id),))
        row = rows[0] if rows else None
        return self._row_to_thread_dict(row) if row else None

    def create_chat(self, community_id, faq_id, title, neighbor_id, technician_id=None) -> str:
        new_id = self.db.insert(
            table="chat_thread",
            data={
                "community_id": int(community_id),
                "created_by_user_id": int(neighbor_id),
                "assigned_user_id": int(technician_id) if technician_id is not None else None,
                "subject": str(title),
                "status": "OPEN",
            },
        )
        return str(new_id)

    def resolve_chat(self, chat_id: int | str) -> None:
        self.db.update(
            table="chat_thread",
            data={
                "status": "CLOSED",
                "closed_at": datetime.now(),
            },
            where={"thread_id": int(chat_id)},
        )

    def update_chat_assignment_and_status(
        self,
        chat_id: int | str,
        *,
        assigned_user_id: int | None = None,
        status: str | None = None,
    ) -> None:
        payload: dict[str, Any] = {}
        if assigned_user_id is not None:
            payload["assigned_user_id"] = int(assigned_user_id)
        if status is not None:
            payload["status"] = str(status)
        if not payload:
            return
        self.db.update(
            table="chat_thread",
            data=payload,
            where={"thread_id": int(chat_id)},
        )

    def get_messages(self, chat_id: int | str) -> List[Dict[str, Any]]:
        sql = """
            SELECT
                cm.message_id,
                cm.thread_id,
                cm.sender_user_id,
                cm.content,
                cm.message_type,
                cm.sent_at,
                u.role AS sender_role,
                u.full_name AS sender_name
            FROM chat_message cm
            INNER JOIN user u
                ON u.user_id = cm.sender_user_id
            WHERE cm.thread_id = %s
            ORDER BY cm.sent_at ASC, cm.message_id ASC
        """
        rows = self.db.execute(sql, (int(chat_id),))
        return [self._row_to_message_dict(row) for row in rows]

    def add_message(self, chat_id, sender_id, sender_role, text) -> None:
        normalized_type = "TEXT"
        self.db.insert(
            table="chat_message",
            data={
                "thread_id": int(chat_id),
                "sender_user_id": int(sender_id),
                "content": str(text),
                "message_type": normalized_type,
            },
        )
