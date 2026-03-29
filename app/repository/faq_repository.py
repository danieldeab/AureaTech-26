from __future__ import annotations
from typing import List, Dict, Any, Optional
from app.infraestructure.db import get_db


class FAQRepository:
    """
    MariaDB-backed FAQ repository.

    Returns compatibility dicts expected by DashboardController/FaqsView.
    """

    def __init__(self):
        self.db = get_db()

    def _row_to_faq_dict(self, row: dict) -> Dict[str, Any]:
        return {
            "id": row["faq_id"],
            "community_id": row["community_id"],
            "question": row["question"],
            "answer": row["answer"],
            "tags": row.get("tags"),
            "is_active": bool(row.get("is_active", 1)),
            "created_at": row.get("created_at"),
        }

    def find_by_community_id(self, community_id: int | str) -> List[Dict[str, Any]]:
        rows = self.db.fetch_all(
            table="faq",
            where={
                "community_id": int(community_id),
                "is_active": 1,
            },
            order_by="faq_id ASC",
        )
        return [self._row_to_faq_dict(row) for row in rows]

    def find_by_id(self, faq_id: int | str) -> Optional[Dict[str, Any]]:
        row = self.db.fetch_one(
            table="faq",
            where={"faq_id": int(faq_id)},
        )
        return self._row_to_faq_dict(row) if row else None