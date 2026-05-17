from __future__ import annotations

from typing import Dict, List, Optional

from app.infraestructure.db import get_db
from app.repository.interfaces.soporte_repository_interface import ISoporteRepository


class SoporteRepository(ISoporteRepository):
    """
    MariaDB-backed repository for Centro de Soporte.

    Source of truth:
    - table: centro de soporte
    - columns:
        centro_soporte_id, nombre_centro, nivel_soporte, created_at
    """

    def __init__(self):
        self.db = get_db()

    # --------------------------------------------------
    # Mapping helpers
    # --------------------------------------------------

    def _soporte_to_db_data(self, soporte: Dict) -> dict:
        return {
            "nombre_centro": soporte["nombre_centro"],
            "nivel_soporte": soporte["nivel_soporte"],
        }

    # --------------------------------------------------
    # Interface API
    # --------------------------------------------------
    def add_soporte(self, soporte: Dict) -> None:
        new_id = self.db.insert(
            table="centro_soporte",
            data=self._soporte_to_db_data(soporte),
        )
        soporte["centro_soporte_id"] = new_id

    def find_by_id(self, soporte_id: str | int) -> Optional[Dict]:
        row = self.db.fetch_one(
            table="centro_soporte",
            where={"centro_soporte_id": int(soporte_id)},
        )
        return row if row else None

    def get_all(self) -> List[Dict]:
        rows = self.db.fetch_all(
            table="centro_soporte",
            order_by="centro_soporte_id ASC",
        )
        return [row for row in rows]

    def save(self, soporte: Dict) -> None:
        if soporte["centro_soporte_id"] is None:
            self.add_soporte(soporte)
            return

        self.db.update(
            table="centro_soporte",
            data=self._soporte_to_db_data(soporte),
            where={"centro_soporte_id": soporte["centro_soporte_id"]},
        )