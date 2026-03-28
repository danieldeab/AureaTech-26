import json
import os
from typing import List, Optional
from uuid import UUID, uuid4

from datetime import datetime, timezone

from app.model.actuator import Actuator
from app.repository.interfaces.actuator_repository_interface import IActuatorRepository

_PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(_PACKAGE_ROOT, "data")
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
        #Descomentar código debajo tras revisión, parte de migración a bbdd
        """
        data = self.db.select("actuators",  "*", "*") #Parte nueva tras migración
        for row in data:
            return [Actuator(data[0], data[1], data[2], data[3], data[4])]

        """

    #Este método ya no tiene sentido tras la migración
    """ 
    def write_all(self) -> None:
        #Force write all actuators to disk.
        with open(ACTUATORS_PATH, "w", encoding="utf-8") as f:
            json.dump([a.to_dict() for a in self.actuators], f, indent=2)
            
    """



    def add(self, actuator: Actuator) -> None:
        # Add new actuator and persist.
        # Ensure valid ID
        if not getattr(actuator, "id", None):
            actuator.id = uuid4()

        # Ensure timestamp is timezone-aware
        if not actuator.lastChangedAt:
            actuator.lastChangedAt = datetime.now(timezone.utc)
        elif isinstance(actuator.lastChangedAt, str):
            actuator.lastChangedAt = datetime.fromisoformat(actuator.lastChangedAt)

        #Descomentar debajo tras revisar, migración a bbdd
        # data = [actuator.id, actuator.name, actuator.type, actuator.state, actuator.lastChangedAt]
        # self.db.add(data)


def findAll(self) -> List[Actuator]:
    """
    #Return all actuators.

    return list(self.actuators)"""

    #Descomentar debajo tras revisión, nuevo código migración a bbdd

    """
    actuators: list[Actuator] = []
    data = self.db.select("actuators", "*", "*")

    for row in data:
        actuators.append(Actuator(row[0], row[1], row[2], row[3], row[4]))
        
    """


def findById(self, actuator_id: int | UUID) -> Optional[Actuator]:
    """#Find actuator by its ID.
    aid = str(actuator_id)
    for a in self.actuators:
        if str(a.id) == aid:
            return a
    return None"""

    #Descomentar debajo tras revisión, nuevo código migración a bbdd
    """
    response = db.select("actuators", "actuator_id", actuator_id) // nombre tabla, columna a la que accede, fila a la que accede
    if response.size() != 0:
        return Actuator(response.get(0), response.get(1), response.get(2), response.get(3), response.get(4))
    else:
        return None
        
    """


def save(self, actuator: Actuator) -> None:

    """Persist a single actuator update."""
    """
    for idx, stored in enumerate(self.actuators):
        if str(stored.id) == str(actuator.id):
            self.actuators[idx] = actuator
            break
    self.write_all()
    
    #Descomentar debajo tras revisión, nuevo código migración a bbdd
    """
    existing = self.db.select("actuators", "id", str(actuator.id))

    if existing:
        self.db.update("actuators", "id", str(actuator.id), actuator.to_row())
    else:
        self.db.insert("actuators", actuator.to_row())
