# app/models/actuator.py

import uuid
from datetime import datetime

class Actuator:
    """Entidad de actuador básica para Sprint 3."""

    def __init__(self, 
                 type: str,
                 state: bool = False):
        
        self._id = str(uuid.uuid4())            # siempre aleatorio
        self._type = type
        self._state = state
        self._lastChangedAt = datetime.now(datetime.timezone.utc)

    # ---------- GETTERS ----------
    def get_id(self):
        return self._id

    def get_type(self):
        return self._type

    def get_state(self):
        return self._state

    def get_last_changed_at(self):
        return self._lastChangedAt


    # ---------- MÉTODOS ----------
    def toggle(self):
        """Invierte el estado del actuador y actualiza lastChangedAt."""
        self._state = not self._state
        self._lastChangedAt = datetime.now(datetime.timezone.utc)

    def set_state(self, new_state: bool):
        """Cambia el estado explícitamente."""
        if self._state != new_state:
            self._state = new_state
            self._lastChangedAt = datetime.now(datetime.timezone.utc)

    def to_dict(self):
        return {
            "id": self._id,
            "type": self._type,
            "state": self._state,
            "lastChangedAt": self._lastChangedAt.isoformat(),
        }
