from typing import List, Optional
from uuid import UUID

from datetime import datetime, timezone

from app.infraestructure.db import get_db
from app.model.actuator import Actuator
from app.repository.interfaces.actuator_repository_interface import IActuatorRepository

class ActuatorRepository(IActuatorRepository):
    """
    MariaDB-backed repository for Actuator.

    DB source of truth:
    - table: actuator
    - columns:
        actuator_id, community_id, actuator_type, location,
        current_state, created_at, last_changed_at

    Compatibility notes:
    - The current Actuator model includes `name`, but the DB schema does not.
      We derive a stable placeholder name at read time.
    - The current model expects boolean `state`; DB stores string `current_state`.
    """

    def __init__(self):
        self.db = get_db()

    # --------------------------------------------------
    # Mapping helpers
    # --------------------------------------------------
    def _db_state_to_bool(self, raw_state) -> bool:
        if isinstance(raw_state, bool):
            return raw_state

        if raw_state is None:
            return False

        normalized = str(raw_state).strip().upper()
        return normalized in {"1", "TRUE", "ON", "OPEN", "ACTIVE", "ENABLED"}

    def _bool_to_db_state(self, state: bool) -> str:
        return "ON" if bool(state) else "OFF"

    def _row_to_actuator(self, row: dict) -> Actuator:
        actuator_id = row["actuator_id"]
        actuator_type = row["actuator_type"]

        return Actuator(
            id=actuator_id,
            name=f"{actuator_type}_{actuator_id}",
            type=actuator_type,
            location=row["location"],
            community_id=row["community_id"],
            state=self._db_state_to_bool(row["current_state"]),
            created_at=row["created_at"],
            lastChangedAt=row["last_changed_at"],
        )

    def _actuator_to_db_data(self, actuator: Actuator) -> dict:
        return {
            "community_id": actuator.community_id,
            "actuator_type": actuator.type,
            "location": actuator.location,
            "current_state": self._bool_to_db_state(actuator.state),
        }

    # --------------------------------------------------
    # Interface API
    # --------------------------------------------------
    def add(self, actuator: Actuator) -> None:
        new_id = self.db.insert(
            table="actuator",
            data=self._actuator_to_db_data(actuator),
        )
        actuator.id = new_id

    def findAll(self) -> List[Actuator]:
        rows = self.db.fetch_all(
            table="actuator",
            order_by="actuator_id ASC",
        )
        return [self._row_to_actuator(row) for row in rows]

    def findById(self, actuator_id: str | int | UUID) -> Optional[Actuator]:
        row = self.db.fetch_one(
            table="actuator",
            where={"actuator_id": actuator_id},
        )
        return self._row_to_actuator(row) if row else None

    def save(self, actuator: Actuator) -> None:
        if getattr(actuator, "id", None) is None:
            self.add(actuator)
            return

        self.db.update(
            table="actuator",
            data=self._actuator_to_db_data(actuator),
            where={"actuator_id": actuator.id},
        )
