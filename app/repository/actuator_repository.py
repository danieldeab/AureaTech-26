# app/repository/actuator_repository.py

import json
import os
from typing import List, Optional
from uuid import UUID

from datetime import datetime, timezone

from app.model.actuator import Actuator
from app.repository.interfaces.actuator_repository_interface import IActuatorRepository


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
ACTUATORS_PATH = os.path.join(DATA_DIR, "actuators.json")


class ActuatorRepository(IActuatorRepository):
    """
    JSON-backed repository for Actuator dataclass objects.
    Fully compatible with the ActuatorService and the dataclass model.
    """

    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.actuators: List[Actuator] = self._load()

    # ---------------------------------------------------
    # Internal JSON load/save helpers
    # ---------------------------------------------------

    def _load(self) -> List[Actuator]:
        if not os.path.exists(ACTUATORS_PATH):
            return []

        try:
            with open(ACTUATORS_PATH, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except json.JSONDecodeError:
            return []

        cleaned: List[Actuator] = []
        for a in raw:
            try:
                cleaned.append(Actuator.from_dict(a))
            except Exception:
                pass

        return cleaned

    def write_all(self) -> None:
        """Force write all actuators to disk."""
        with open(ACTUATORS_PATH, "w", encoding="utf-8") as f:
            json.dump([a.to_dict() for a in self.actuators], f, indent=2)

    # ---------------------------------------------------
    # Interface Implementations
    # ---------------------------------------------------

    def add(self, actuator: Actuator) -> None:
        """Add new actuator and persist."""
        # Ensure valid ID
        if not getattr(actuator, "id", None):
            actuator.id = uuid.uuid4()

        # Ensure timestamp is timezone-aware
        if not actuator.lastChangedAt:
            actuator.lastChangedAt = datetime.now(timezone.utc)
        elif isinstance(actuator.lastChangedAt, str):
            actuator.lastChangedAt = datetime.fromisoformat(actuator.lastChangedAt)

        self.actuators.append(actuator)
        self.write_all()

    def findAll(self) -> List[Actuator]:
        """Return all actuators."""
        return list(self.actuators)

    def findById(self, actuator_id: str | UUID) -> Optional[Actuator]:
        """Find actuator by its ID."""
        aid = str(actuator_id)
        for a in self.actuators:
            if str(a.id) == aid:
                return a
        return None

    def save(self, actuator: Actuator) -> None:
        """Persist a single actuator update."""
        for idx, stored in enumerate(self.actuators):
            if str(stored.id) == str(actuator.id):
                self.actuators[idx] = actuator
                break
        self.write_all()
