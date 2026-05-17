from __future__ import annotations

from typing import Any, List
from uuid import UUID

from app.infraestructure.db import get_db
from app.model.reading import Reading
from app.repository.interfaces.reading_repository_interface import IReadingRepository


class ReadingRepository(IReadingRepository):
    """
    MariaDB-backed repository for Reading.

    Source of truth:
    - table: reading
    - columns:
        reading_id, sensor_id, reading_value, unit, recorded_at
    """

    def __init__(self):
        self.db = get_db()

    # --------------------------------------------------
    # Mapping helpers
    # --------------------------------------------------
    def _row_to_reading(self, row: dict) -> Reading:
        return Reading(
            id=row["reading_id"],
            sensor_id=row["sensor_id"],
            timestamp=row["recorded_at"],
            value=float(row["reading_value"]),
            unit=row["unit"],
        )

    def _reading_to_db_data(self, reading: Reading) -> dict:
        data = {
            "sensor_id": reading.sensor_id,
            "reading_value": reading.value,
            "unit": reading.unit,
        }
        if getattr(reading, "timestamp", None) is not None:
            data["recorded_at"] = reading.timestamp
        return data

    # --------------------------------------------------
    # Interface API
    # --------------------------------------------------
    def add_reading(self, reading: Reading) -> None:
        new_id = self.db.insert(
            table="reading",
            data=self._reading_to_db_data(reading),
        )
        reading.id = new_id

    def find_by_sensor(self, sensor_id: UUID | int | str) -> List[Reading]:
        rows = self.db.fetch_all(
            table="reading",
            where={"sensor_id": sensor_id},
            order_by="recorded_at DESC",
        )
        return [self._row_to_reading(row) for row in rows]

    def get_all(self) -> List[Reading]:
        rows = self.db.fetch_all(
            table="reading",
            order_by="recorded_at DESC",
        )
        return [self._row_to_reading(row) for row in rows]

    def search(
        self,
        filters: dict[str, Any] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> List[Reading]:
        filters = filters or {}
        where_clauses = ["1=1"]
        params: list[Any] = []

        if filters.get("sensor_id") is not None:
            where_clauses.append("r.sensor_id = %s")
            params.append(int(filters["sensor_id"]))
        if filters.get("community_id") is not None:
            where_clauses.append("s.community_id = %s")
            params.append(int(filters["community_id"]))
        if filters.get("sensor_type"):
            where_clauses.append("s.sensor_type = %s")
            params.append(str(filters["sensor_type"]).upper())
        if filters.get("start_date"):
            where_clauses.append("r.recorded_at >= %s")
            params.append(filters["start_date"])
        if filters.get("end_date"):
            where_clauses.append("r.recorded_at <= %s")
            params.append(filters["end_date"])

        sql = """
            SELECT
                r.reading_id,
                r.sensor_id,
                r.reading_value,
                r.unit,
                r.recorded_at
            FROM reading r
            INNER JOIN sensor s
                ON s.sensor_id = r.sensor_id
            WHERE {where_sql}
            ORDER BY r.recorded_at DESC, r.reading_id DESC
        """.format(where_sql=" AND ".join(where_clauses))

        if limit is not None:
            sql += " LIMIT %s"
            params.append(int(limit))
            if offset is not None:
                sql += " OFFSET %s"
                params.append(int(offset))

        rows = self.db.execute(sql, tuple(params))
        return [self._row_to_reading(row) for row in rows]
