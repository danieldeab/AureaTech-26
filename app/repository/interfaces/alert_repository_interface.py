# app/repository/interfaces/IAlertRepository.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from app.model.alert import Alert
from app.model.user_alert import UserAlert

class IAlertRepository(ABC):

    @abstractmethod
    def add_alert(self, alert: Alert) -> Alert:
        #Añade una alerta a la colección
        pass

    @abstractmethod
    def find_alert_by_id(self, alert_id: int) -> Optional[Alert]:
        pass

    @abstractmethod
    def get_all_alerts(self) -> List[Alert]:
        pass

    @abstractmethod
    def get_alerts_for_community(self, community_id: int) -> List[Alert]:
        pass

    # --------------------------------------------------
    # USER_ALERT (delivery/read entity)
    # --------------------------------------------------
    @abstractmethod
    def add_user_alert(self, user_alert: UserAlert) -> UserAlert:
        pass

    @abstractmethod
    def find_user_alert_by_id(self, user_alert_id: int) -> Optional[UserAlert]:
        pass

    @abstractmethod
    def find_user_alert(self, user_id: int, alert_id: int) -> Optional[UserAlert]:
        pass

    @abstractmethod
    def mark_user_alert_read(self, user_id: int, alert_id: int) -> bool:
        pass

    @abstractmethod
    def get_user_alerts(self, user_id: int) -> List[UserAlert]:
        pass

    # --------------------------------------------------
    # JOINED / READ-MODEL QUERIES
    # --------------------------------------------------
    @abstractmethod
    def get_alert_deliveries_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Returns joined alert + user_alert information, suitable for services/UI.
        """
        pass

    # Legacy / transitional methods for service compatibility with older repository APIs.

    @abstractmethod
    def find_by_id(self, alert_id: str) -> Optional[Alert]:
        #Busca una alerta por ID
        pass

    @abstractmethod
    def get_all(self) -> List[Alert]:
        #Devuelve todas las alertas cargadas
        pass
