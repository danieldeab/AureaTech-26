# app/repository/interfaces/IAlertRepository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from app.model.alert import Alert


class IAlertRepository(ABC):

    @abstractmethod
    def add_alert(self, alert: Alert) -> None:
        """Añade una alerta a la colección."""
        pass

    @abstractmethod
    def find_by_id(self, alert_id: str) -> Optional[Alert]:
        """Busca una alerta por ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[Alert]:
        """Devuelve todas las alertas cargadas."""
        pass

    @abstractmethod
    def save(self) -> None:
        """Guarda todas las alertas en el archivo JSON."""
        pass
