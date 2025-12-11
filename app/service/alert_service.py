# app/service/alert_service.py

from typing import List, Optional, Union
from uuid import UUID

from app.model.alert import Alert
from app.model.sensor import Reading
from app.model.enums import SeverityEnum
from app.repository.interfaces.alert_repository_interface import IAlertRepository
from app.repository.alert_repository import AlertRepository


AlertId = Union[str, UUID]
UserId = Union[str, UUID]


class AlertService:
    """
    Application-layer service for alerts.

    Responsibilities (aligned with the class diagram):
      - Evaluate a Reading and (optionally) create an Alert.
      - Mark alerts as read for a given user.
      - Query alerts for a given user or globally.

    It depends on an alert repository interface, which keeps
    persistence details out of the service (Dependency Inversion).
    """

    def __init__(self, repo: IAlertRepository):
        self._repo = repo

    # --------------------------------------------------
    # Core business logic
    # --------------------------------------------------

    def evaluate(self, reading: Reading) -> Optional[Alert]:
        """
        Evaluates a sensor reading and, if thresholds are exceeded,
        creates and persists an Alert.

        Returns:
            The created Alert, or None if no alert is generated.
        """
        alert: Optional[Alert] = None

        sensor_type = getattr(reading, "sensor_type", "").lower()
        value = getattr(reading, "value", 0)
        sensor_id = getattr(reading, "sensor_id", None)
        user_id = getattr(reading, "user_id", None)

        # If we don't know which user this belongs to, we don't create
        # a user-targeted alert yet.
        if not user_id:
            return None

        # -----------------------------
        # Temperature
        # -----------------------------
        if sensor_type == "temperature":
            if value > 30:
                alert = Alert.new(
                    type="high_temperature",
                    severity=SeverityEnum.HIGH,
                    message=f"Temperatura crítica detectada: {value}°C",
                    target_user_id=user_id,
                )
            elif value < 10:
                alert = Alert.new(
                    type="low_temperature",
                    severity=SeverityEnum.MEDIUM,
                    message=f"Temperatura baja detectada: {value}°C",
                    target_user_id=user_id,
                )

        # -----------------------------
        # Humidity
        # -----------------------------
        elif sensor_type == "humidity":
            if value > 80:
                alert = Alert.new(
                    type="high_humidity",
                    severity=SeverityEnum.MEDIUM,
                    message=f"Humedad alta detectada: {value}%",
                    target_user_id=user_id,
                )
            elif value < 20:
                alert = Alert.new(
                    type="low_humidity",
                    severity=SeverityEnum.LOW,
                    message=f"Humedad baja detectada: {value}%",
                    target_user_id=user_id,
                )

        # -----------------------------
        # Air quality
        # -----------------------------
        elif sensor_type in ("air_quality", "co2"):
            if value > 150:
                alert = Alert.new(
                    type="poor_air_quality",
                    severity=SeverityEnum.HIGH,
                    message=f"Calidad del aire deficiente: {value} AQI/ppm",
                    target_user_id=user_id,
                )

        # -----------------------------
        # Light
        # -----------------------------
        elif sensor_type == "light":
            if value < 100:
                alert = Alert.new(
                    type="low_light",
                    severity=SeverityEnum.LOW,
                    message=f"Nivel de luz bajo: {value} lux",
                    target_user_id=user_id,
                )

        # If an alert was generated, persist it via the repository
        if alert:
            self._repo.add_alert(alert)
            self._repo.save()

        return alert

    # --------------------------------------------------
    # Read / write operations
    # --------------------------------------------------

    def mark_read(self, alert_id: AlertId, user_id: UserId) -> None:
        """
        Mark an alert as read, but only if it belongs to the given user.
        """
        try:
            alert_uuid = UUID(alert_id) if isinstance(alert_id, str) else alert_id
        except (ValueError, TypeError, AttributeError):
            return

        alert = self._repo.find_by_id(str(alert_uuid))
        if not alert:
            return

        # Ensure the caller is the intended recipient
        try:
            user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id
        except (ValueError, TypeError, AttributeError):
            return

        if str(alert.target_user_id) != str(user_uuid):
            return

        alert.read_status = True
        self._repo.save()

    def get_alerts(self, user_id: UserId) -> List[Alert]:
        """
        Return all alerts for a specific user, sorted from most recent to oldest.
        """
        try:
            user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id
        except (ValueError, TypeError, AttributeError):
            return []

        all_alerts = self._repo.get_all()

        user_alerts = [
            alert
            for alert in all_alerts
            if str(alert.target_user_id) == str(user_uuid)
        ]

        # Sort by timestamp (newest first)
        user_alerts.sort(key=lambda a: getattr(a, "timestamp", None), reverse=True)
        return user_alerts

    def get_all_alerts(self) -> List[Alert]:
        """
        Return all alerts, sorted from most recent to oldest.

        This is what your DashboardController is currently using
        to feed the alerts view.
        """
        alerts = self._repo.get_all()
        alerts.sort(key=lambda a: getattr(a, "timestamp", None), reverse=True)
        return alerts

    def get_alerts_for_community(self, community_id: int):
        """
        Returns all alerts that belong to a given community.
        Works with alerts produced by MonitoringService (community-level)
        AND alerts targeted to a specific user in that community.
        """
        alerts = self._repo.get_all()
        community_id = int(community_id)

        results = []
        for a in alerts:
            # Case 1: MonitoringService assigned target_user_id = community_id
            if str(a.target_user_id) == str(community_id):
                results.append(a)
                continue

            # Case 2: Check metadata (if present)
            meta = getattr(a, "metadata", {}) or {}
            if str(meta.get("community_id")) == str(community_id):
                results.append(a)

        # Newest first
        results.sort(key=lambda x: x.timestamp, reverse=True)
        return results

    def get_alerts_for_technician(self, community_id: int):
        """
        Technicians get the same community alerts as admins
        (but only for their own community).
        """
        return self.get_alerts_for_community(community_id)



# ======================================================
# Backwards-compatible functional API
# ======================================================

# Default singleton service used by the old free functions
_default_service = AlertService(AlertRepository())


def evaluate(reading: Reading) -> Optional[Alert]:
    """
    Legacy free function kept for compatibility.

    Delegates to the default AlertService instance.
    Used by monitoring_service.
    """
    return _default_service.evaluate(reading)


def markRead(alertId: str, userId: str) -> None:
    """
    Legacy free function kept for compatibility.
    """
    _default_service.mark_read(alertId, userId)


def getAlerts(userId: str) -> List[Alert]:
    """
    Legacy free function kept for compatibility.
    """
    return _default_service.get_alerts(userId)
