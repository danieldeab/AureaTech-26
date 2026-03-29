# app/repository/interfaces/actuator_repository_interface.py

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.model.actuator import Actuator


class IActuatorRepository(ABC):
    """
    Interface definition for actuator repositories.
    Concrete implementations must handle persistence,
    deserialization and storage of Actuator objects.
    """

    @abstractmethod
    def add(self, actuator: Actuator) -> None:
        """Add a new actuator."""

    @abstractmethod
    def findAll(self) -> List[Actuator]:
        """Return all actuators."""

    @abstractmethod
    def findById(self, actuator_id: str | UUID) -> Optional[Actuator]:
        """Find a single actuator by its ID."""

    @abstractmethod
    def save(self, actuator: Actuator) -> None:
        """Persist updates to an existing actuator."""

