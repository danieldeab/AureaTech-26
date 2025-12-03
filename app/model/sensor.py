from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict
from uuid import UUID, uuid4


@dataclass(slots=True)
class Sensor:
    """
    Domain model for a physical / simulated sensor in the AureaTech system.

    - id: stable UUID used as primary key across JSON, repositories and UI.
    - type: logical sensor type (e.g. 'DHT22', 'LDR', 'HC-SR04').
    - location: human-readable location ('Salón', 'Garaje', 'Patio', etc.).
    - thresholds: optional mapping of metric -> limit (e.g. {'temp_max': 28.0}).
    """
    id: UUID
    type: str
    location: str
    thresholds: Dict[str, float] = field(default_factory=dict)

    @staticmethod
    def new(type: str, location: str, thresholds: Dict[str, float] | None = None) -> "Sensor":
        return Sensor(id=uuid4(), type=type, location=location, thresholds=thresholds or {})

    def to_dict(self) -> dict:
        """
        JSON-serializable representation for persistence on sensores.json.
        """
        d = asdict(self)
        d["id"] = str(self.id)
        return d

    @staticmethod
    def from_dict(d: dict) -> "Sensor":
        """
        Factory to reconstruct a Sensor from a dict loaded from JSON.
        """
        from uuid import UUID
        return Sensor(
            id=UUID(d["id"]),
            type=d["type"],
            location=d["location"],
            thresholds=d.get("thresholds", {}),
        )
