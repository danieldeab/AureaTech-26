from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Union, Iterable, Dict, Any

from app.model.alert import Alert
from app.model.user_alert import UserAlert
from app.model.reading import Reading
from app.model.enums import SeverityEnum
from app.repository.interfaces.alert_repository_interface import IAlertRepository
from app.repository.alert_repository import AlertRepository


AlertId = Union[str, int]
UserId = Union[str, int]


class AlertService:
    """
    Application-layer service for relational alerts.

    Responsibilities:
      - create Alert events
      - create UserAlert deliveries
      - mark user alerts as read
      - expose community alerts and user-facing joined alert deliveries

    The service is now the translation boundary between:
      - DB-faithful entities (Alert, UserAlert)
      - UI/application-facing read models (dicts)
    """

    def __init__(self, repo: IAlertRepository):
        self._repo = repo

    # --------------------------------------------------
    # Internal helpers
    # --------------------------------------------------
    def _normalize_int(self, value) -> Optional[int]:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _severity_for_sensor_value(
        self,
        *,
        sensor_type: str,
        value: float,
    ) -> Optional[SeverityEnum]:
        st = sensor_type.lower()

        if st == "temperature":
            if value > 30:
                return SeverityEnum.CRIT
            if value < 10:
                return SeverityEnum.WARN
            return None

        if st == "humidity":
            if value > 80:
                return SeverityEnum.WARN
            if value < 20:
                return SeverityEnum.INFO
            return None

        if st in ("air_quality", "co2", "smoke"):
            if value > 150:
                return SeverityEnum.CRIT
            return None

        if st == "light":
            if value < 100:
                return SeverityEnum.INFO
            return None

        return None

    def _alert_type_for_sensor_value(
        self,
        *,
        sensor_type: str,
        value: float,
    ) -> Optional[str]:
        st = sensor_type.lower()

        if st == "temperature":
            if value > 30:
                return "high_temperature"
            if value < 10:
                return "low_temperature"
            return None

        if st == "humidity":
            if value > 80:
                return "high_humidity"
            if value < 20:
                return "low_humidity"
            return None

        if st in ("air_quality", "co2", "smoke"):
            if value > 150:
                return "poor_air_quality"
            return None

        if st == "light":
            if value < 100:
                return "low_light"
            return None

        return None

    def _message_for_sensor_value(
        self,
        *,
        sensor_type: str,
        value: float,
    ) -> Optional[str]:
        st = sensor_type.lower()

        if st == "temperature":
            if value > 30:
                return f"Temperatura crítica detectada: {value}°C"
            if value < 10:
                return f"Temperatura baja detectada: {value}°C"
            return None

        if st == "humidity":
            if value > 80:
                return f"Humedad alta detectada: {value}%"
            if value < 20:
                return f"Humedad baja detectada: {value}%"
            return None

        if st in ("air_quality", "co2", "smoke"):
            if value > 150:
                return f"Calidad del aire deficiente: {value} AQI/ppm"
            return None

        if st == "light":
            if value < 100:
                return f"Nivel de luz bajo: {value} lux"
            return None

        return None

    def _guess_rule_alert_action_id(
        self,
        *,
        alert_type: str,
    ) -> int:
        """
        Temporary compatibility helper.

        Because the current service layer still creates alerts from business logic
        rather than by resolving real automation rule actions first, we use a small
        deterministic mapping to stay compatible with the seeded schema.

        Replace this later with a real lookup if you introduce a RuleAlertActionRepository.
        """
        mapping = {
            "high_temperature": 1,
            "low_light": 2,
            "poor_air_quality": 3,
            # temporary fallbacks not present in current seed but allowed structurally
            "low_temperature": 1,
            "high_humidity": 1,
            "low_humidity": 1,
            "streetlight_automation": 2,
            "unauthorized_plate": 1,
        }
        return mapping.get(alert_type, 1)

    # --------------------------------------------------
    # Creation API
    # --------------------------------------------------
    def create_alert(
        self,
        *,
        community_id: int,
        rule_alert_action_id: int,
        alert_type: str,
        severity: SeverityEnum,
        message: str,
    ) -> Alert:
        alert = Alert.new(
            community_id=community_id,
            rule_alert_action_id=rule_alert_action_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
        )
        return self._repo.add_alert(alert)

    def deliver_alert_to_user(
        self,
        *,
        user_id: int,
        alert_id: int,
    ) -> UserAlert:
        existing = self._repo.find_user_alert(user_id, alert_id)
        if existing:
            return existing

        user_alert = UserAlert.new(
            user_id=user_id,
            alert_id=alert_id,
            read_status=False,
            read_at=None,
        )
        return self._repo.add_user_alert(user_alert)

    def deliver_alert_to_users(
        self,
        *,
        alert_id: int,
        user_ids: Iterable[int],
    ) -> List[UserAlert]:
        deliveries: List[UserAlert] = []
        for raw_uid in user_ids:
            uid = self._normalize_int(raw_uid)
            if uid is None:
                continue
            deliveries.append(
                self.deliver_alert_to_user(user_id=uid, alert_id=alert_id)
            )
        return deliveries

    def create_and_deliver_alert(
        self,
        *,
        community_id: int,
        recipients: Iterable[int],
        alert_type: str,
        severity: SeverityEnum,
        message: str,
        rule_alert_action_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        action_id = (
            int(rule_alert_action_id)
            if rule_alert_action_id is not None
            else self._guess_rule_alert_action_id(alert_type=alert_type)
        )

        alert = self.create_alert(
            community_id=community_id,
            rule_alert_action_id=action_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
        )

        deliveries = self.deliver_alert_to_users(
            alert_id=alert.id,
            user_ids=recipients,
        )

        return {
            "alert": alert,
            "deliveries": deliveries,
        }

    # --------------------------------------------------
    # Reading-based evaluation
    # --------------------------------------------------
    def evaluate(self, reading: Reading) -> Optional[Dict[str, Any]]:
        """
        Evaluates a reading and, if thresholds are exceeded, creates:
          - one Alert event
          - one or more UserAlert deliveries

        Expected dynamic attributes on reading for now:
          - sensor_type
          - community_id
          - user_id OR recipient_user_ids

        This keeps the service compatible with the current partially-migrated codebase.
        """
        sensor_type = str(getattr(reading, "sensor_type", "")).strip()
        if not sensor_type:
            return None

        value = getattr(reading, "value", None)
        if value is None:
            return None

        alert_type = self._alert_type_for_sensor_value(
            sensor_type=sensor_type,
            value=value,
        )
        severity = self._severity_for_sensor_value(
            sensor_type=sensor_type,
            value=value,
        )
        message = self._message_for_sensor_value(
            sensor_type=sensor_type,
            value=value,
        )

        if not alert_type or not severity or not message:
            return None

        community_id = self._normalize_int(getattr(reading, "community_id", None))
        if community_id is None:
            return None

        recipient_user_ids = getattr(reading, "recipient_user_ids", None)
        if recipient_user_ids is None:
            single_user_id = self._normalize_int(getattr(reading, "user_id", None))
            if single_user_id is None:
                return None
            recipient_user_ids = [single_user_id]

        return self.create_and_deliver_alert(
            community_id=community_id,
            recipients=recipient_user_ids,
            alert_type=alert_type,
            severity=severity,
            message=message,
        )

    # --------------------------------------------------
    # Read / write operations
    # --------------------------------------------------
    def mark_read(self, alert_id: AlertId, user_id: UserId) -> bool:
        aid = self._normalize_int(alert_id)
        uid = self._normalize_int(user_id)
        if aid is None or uid is None:
            return False

        return self._repo.mark_user_alert_read(uid, aid)

    def get_alert_deliveries_for_user(self, user_id: UserId) -> List[Dict[str, Any]]:
        uid = self._normalize_int(user_id)
        if uid is None:
            return []
        return self._repo.get_alert_deliveries_for_user(uid)

    def get_alerts(self, user_id: UserId) -> List[Dict[str, Any]]:
        """
        User-facing query.
        Returns joined alert+user_alert read models, not raw Alert entities.
        """
        return self.get_alert_deliveries_for_user(user_id)

    def get_all_alerts(self) -> List[Alert]:
        return self._repo.get_all_alerts()

    def get_alerts_for_community(self, community_id: int) -> List[Alert]:
        cid = self._normalize_int(community_id)
        if cid is None:
            return []
        return self._repo.get_alerts_for_community(cid)

    def get_alerts_for_technician(self, community_id: int) -> List[Alert]:
        return self.get_alerts_for_community(community_id)

    # --------------------------------------------------
    # Automation helper used by dashboard/controller flow
    # --------------------------------------------------
    def apply_streetlight_decision(self, decision: dict) -> Optional[Dict[str, Any]]:
        """
        Creates a community alert when streetlight automation turns lights on.

        NOTE:
        This only creates the Alert event for now.
        It does not yet fan-out to all community users automatically because
        the current service layer does not yet have a UserRepository dependency.
        """
        if not decision:
            return None

        community_id = self._normalize_int(decision.get("community_id"))
        desired = bool(decision.get("streetlights_on"))

        if community_id is None or not desired:
            return None

        reason = decision.get("reason", {}) or {}
        ldr = reason.get("ldr")
        distance = reason.get("distance")

        message = (
            f"Encendido automático de farolas en comunidad {community_id} "
            f"(oscuro={ldr}, distancia={distance})"
        )

        alert = self.create_alert(
            community_id=community_id,
            rule_alert_action_id=self._guess_rule_alert_action_id(
                alert_type="streetlight_automation"
            ),
            alert_type="streetlight_automation",
            severity=SeverityEnum.INFO,
            message=message,
        )

        return {
            "alert": alert,
            "deliveries": [],
        }


# ======================================================
# Backwards-compatible functional API
# ======================================================

_default_service = AlertService(AlertRepository())


def evaluate(reading: Reading):
    return _default_service.evaluate(reading)


def markRead(alertId, userId) -> None:
    _default_service.mark_read(alertId, userId)


def getAlerts(userId):
    return _default_service.get_alerts(userId)
