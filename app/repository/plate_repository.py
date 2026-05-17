from __future__ import annotations

from datetime import datetime
from typing import Any

from app.infraestructure.db import get_db


class PlateRepository:
    """
    DB boundary for license-plate recognition.

    Tables:
    - allowed_plate
    - camera_event
    - sensor
    """

    def __init__(self):
        self.db = get_db()

    def get_sensor_community_id(self, sensor_id: int) -> int | None:
        row = self.db.fetch_one(
            table="sensor",
            columns=["community_id"],
            where={"sensor_id": int(sensor_id)},
        )
        return int(row["community_id"]) if row and row.get("community_id") is not None else None

    def find_allowed_plate(self, plate: str, community_id: int) -> dict[str, Any] | None:
        sql = """
            SELECT
                ap.allowed_plate_id,
                ap.community_id,
                ap.user_id,
                ap.plate,
                ap.is_active,
                ap.created_at,
                u.role AS owner_role,
                u.community_id AS owner_community_id
            FROM allowed_plate ap
            INNER JOIN user u
                ON u.user_id = ap.user_id
            WHERE ap.plate = %s
              AND ap.is_active = 1
              AND u.is_active = 1
              AND (
                    u.role = 'ADMIN'
                    OR (
                        u.role IN ('NEIGHBOR', 'TECHNICIAN')
                        AND u.community_id = %s
                        AND ap.community_id = %s
                    )
              )
            ORDER BY
                CASE WHEN u.role = 'ADMIN' THEN 0 ELSE 1 END,
                ap.allowed_plate_id ASC
            LIMIT 1
        """
        rows = self.db.execute(sql, (normalize_plate(plate), int(community_id), int(community_id)))
        return rows[0] if rows else None

    def list_user_plates(self, user_id: int) -> list[dict[str, Any]]:
        rows = self.db.fetch_all(
            table="allowed_plate",
            where={"user_id": int(user_id)},
            order_by="created_at DESC",
        )
        return [self._plate_row_to_dict(row) for row in rows]

    def list_pending_plates(self, community_id: int | None = None) -> list[dict[str, Any]]:
        filters: dict[str, Any] = {"is_active": 0}
        if community_id is not None:
            filters["community_id"] = int(community_id)
        rows = self.db.fetch_all(
            table="allowed_plate",
            where=filters,
            order_by="created_at DESC",
        )
        return [self._plate_row_to_dict(row) for row in rows]

    def request_plate(self, *, user_id: int, community_id: int, plate: str) -> int:
        return self.db.insert(
            table="allowed_plate",
            data={
                "community_id": int(community_id),
                "user_id": int(user_id),
                "plate": normalize_plate(plate),
                "is_active": 0,
            },
        )

    def approve_plate(self, allowed_plate_id: int) -> int:
        return self.db.update(
            table="allowed_plate",
            data={"is_active": 1},
            where={"allowed_plate_id": int(allowed_plate_id)},
        )

    def deactivate_plate(self, allowed_plate_id: int, user_id: int | None = None) -> int:
        where: dict[str, Any] = {"allowed_plate_id": int(allowed_plate_id)}
        if user_id is not None:
            where["user_id"] = int(user_id)
        return self.db.update(
            table="allowed_plate",
            data={"is_active": 0},
            where=where,
        )

    def delete_plate(self, allowed_plate_id: int) -> int:
        return self.db.delete(
            table="allowed_plate",
            where={"allowed_plate_id": int(allowed_plate_id)},
        )

    def add_camera_event(
        self,
        *,
        sensor_id: int,
        detected_plate: str,
        is_allowed: bool,
        detected_at: datetime,
        image_path: str | None = None,
    ) -> int:
        return self.db.insert(
            table="camera_event",
            data={
                "sensor_id": int(sensor_id),
                "detected_plate": normalize_plate(detected_plate),
                "is_allowed": int(bool(is_allowed)),
                "detected_at": detected_at,
                "image_path": image_path,
            },
        )

    def search_camera_events(
        self,
        filters: dict[str, Any] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        filters = filters or {}
        where_clauses = ["1=1"]
        params: list[Any] = []

        if filters.get("community_id") is not None:
            where_clauses.append("s.community_id = %s")
            params.append(int(filters["community_id"]))
        if filters.get("sensor_id") is not None:
            where_clauses.append("ce.sensor_id = %s")
            params.append(int(filters["sensor_id"]))
        if filters.get("plate"):
            where_clauses.append("ce.detected_plate = %s")
            params.append(normalize_plate(filters["plate"]))
        if filters.get("is_allowed") is not None:
            where_clauses.append("ce.is_allowed = %s")
            params.append(int(bool(filters["is_allowed"])))
        if filters.get("start_date"):
            where_clauses.append("ce.detected_at >= %s")
            params.append(filters["start_date"])
        if filters.get("end_date"):
            where_clauses.append("ce.detected_at <= %s")
            params.append(filters["end_date"])

        sql = """
            SELECT
                ce.camera_event_id,
                ce.sensor_id,
                s.community_id,
                ce.detected_plate,
                ce.is_allowed,
                ce.detected_at,
                ce.image_path
            FROM camera_event ce
            INNER JOIN sensor s
                ON s.sensor_id = ce.sensor_id
            WHERE {where_sql}
            ORDER BY ce.detected_at DESC, ce.camera_event_id DESC
        """.format(where_sql=" AND ".join(where_clauses))

        if limit is not None:
            sql += " LIMIT %s"
            params.append(int(limit))
            if offset is not None:
                sql += " OFFSET %s"
                params.append(int(offset))

        return self.db.execute(sql, tuple(params))

    def _plate_row_to_dict(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "allowed_plate_id": row.get("allowed_plate_id"),
            "community_id": row.get("community_id"),
            "user_id": row.get("user_id"),
            "plate": row.get("plate"),
            "is_active": bool(row.get("is_active")),
            "status": "APPROVED" if bool(row.get("is_active")) else "PENDING",
            "created_at": row.get("created_at"),
        }


def normalize_plate(plate: str) -> str:
    return "".join(str(plate or "").upper().split())
