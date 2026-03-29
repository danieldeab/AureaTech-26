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
        }

    def _row_to_message_dict(self, row: dict) -> Dict[str, Any]:
        return {
            "id": row["message_id"],
            "chat_id": row["thread_id"],
            "sender_id": row["sender_user_id"],
            "sender_role": row["sender_role"],
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
                u.full_name AS neighbor_name
            FROM chat_thread ct
            INNER JOIN user u
                ON u.user_id = ct.created_by_user_id
            WHERE ct.assigned_user_id = %s
            ORDER BY COALESCE(ct.closed_at, ct.created_at) DESC, ct.thread_id DESC
        """
        rows = self.db.execute(sql, (int(technician_id),))
        return [self._row_to_thread_dict(row) for row in rows]

    def get_chat_by_id(self, chat_id: int | str) -> Optional[Dict[str, Any]]:
        row = self.db.fetch_one(
            table="chat_thread",
            where={"thread_id": int(chat_id)},
        )
        return self._row_to_thread_dict(row) if row else None

    def create_chat(self, community_id, faq_id, title, neighbor_id, technician_id) -> str:
        new_id = self.db.insert(
            table="chat_thread",
            data={
                "community_id": int(community_id),
                "created_by_user_id": int(neighbor_id),
                "assigned_user_id": int(technician_id),
                "subject": str(title),
                "status": "OPEN",
            },
        )
        return str(new_id)

    def resolve_chat(self, chat_id: int | str) -> None:
        self.db.update(
            table="chat_thread",
            data={
                "status": "RESOLVED",
                "closed_at": datetime.now(),
            },
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
                u.role AS sender_role
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