from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from typing import Optional, Iterable

from app.model.reading import Reading
from app.model.sensor import Sensor
from app.model.enums import SeverityEnum, RoleEnum

from app.repository.sensor_repository import SensorRepository
from app.repository.reading_repository import ReadingRepository
from app.repository.log_repository import LogRepository

from app.service.alert_service import AlertService
from app.service.audit_log_service import AuditLogService
from app.service.error_service import ErrorService


class MonitoringService:
    """
    Relational monitoring service.

    Responsibilities:
    - read sensors from SensorRepository
    - read latest readings from ReadingRepository
    - evaluate automation decisions
    - create alert events through AlertService
    - write audit logs through LogRepository

    Notes:
    - Sensors do not carry embedded live values anymore.
    - Community-scoped automation decisions are derived from latest readings.
    """

    def __init__(
        self,
        sensor_repo: SensorRepository,
        reading_repo: ReadingRepository,
        alert_service: AlertService,
        log_repo: LogRepository,
        audit_log_service: AuditLogService | None = None,
        error_service: ErrorService | None = None,
        automation_rule_service=None,
    ):
        self.sensor_repo = sensor_repo
        self.reading_repo = reading_repo
        self.alert_service = alert_service
        self.audit_log_service = audit_log_service or AuditLogService(log_repo)
        self.error_service = error_service or ErrorService()
        self.automation_rule_service = automation_rule_service

    # ----------------------------------------------------------------------
    # Internal helpers
    # ----------------------------------------------------------------------
    def _get_sensors_for_community(
        self,
        community_id: int,
    ) -> list[Sensor]:
        sensors = self.sensor_repo.get_all()
        return [
            s for s in sensors
            if s.from_community_id == community_id and bool(getattr(s, "is_enabled", False))
        ]

    def _find_sensor_by_type(
        self,
        sensors: Iterable[Sensor],
        *sensor_types: str,
    ) -> Optional[Sensor]:
        normalized = {st.upper() for st in sensor_types}
        for sensor in sensors:
            if str(sensor.type).upper() in normalized:
                return sensor
        return None

    def _get_latest_reading_for_sensor(
        self,
        sensor_id: int,
    ) -> Optional[Reading]:
        readings = self.reading_repo.find_by_sensor(sensor_id)
        if not readings:
            return None

        # repository already returns DESC by time, but keep defensive sort
        readings = sorted(readings, key=lambda r: r.timestamp, reverse=True)
        return readings[0]

    def _coerce_float(self, value) -> Optional[float]:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _log_automation_event(
        self,
        *,
        action: str,
        details: str,
        actor_id: int = 1,
    ) -> None:
        """
        Temporary system/automation logger.

        Uses actor_id=1 as a system/admin surrogate because audit_log.user_id
        is INT NOT NULL and the current schema has no dedicated nullable system actor.
        """
        self.audit_log_service.log(
            actor_id=actor_id,
            actor_role=RoleEnum.ADMIN,
            category="AUTOMATION",
            action=action,
            details=details,
            target_entity_type="community",
        )

    # ----------------------------------------------------------------------
    # AUTOMATIONS
    # ----------------------------------------------------------------------
    def evaluate_streetlights_for_community(self, community_id: int):
        """
        Streetlight automation rule:
        Turn streetlights ON if:
        - it is dark
        - presence is detected nearby

        Returns only the decision. No side effects here.
        """
        LDR_THRESHOLD = 0.3
        DIST_THRESHOLD = 100.0  # cm

        sensors = self._get_sensors_for_community(community_id)

        light_sensor = self._find_sensor_by_type(sensors, "LIGHT", "LDR")
        distance_sensor = self._find_sensor_by_type(sensors, "DISTANCE")

        if not light_sensor or not distance_sensor:
            return None

        if light_sensor.sensor_id is None or distance_sensor.sensor_id is None:
            return None

        light_reading = self._get_latest_reading_for_sensor(light_sensor.sensor_id)
        distance_reading = self._get_latest_reading_for_sensor(distance_sensor.sensor_id)

        if not light_reading or not distance_reading:
            return None

        light_value = self._coerce_float(light_reading.value)
        distance_value = self._coerce_float(distance_reading.value)

        if light_value is None or distance_value is None:
            return None

        is_dark = light_value < LDR_THRESHOLD
        presence = distance_value < DIST_THRESHOLD
        desired_state = is_dark and presence

        return {
            "community_id": community_id,
            "streetlights_on": desired_state,
            "reason": {
                "ldr": light_value,
                "distance": distance_value,
                "evaluated_at": datetime.now().isoformat(),
            },
        }
    
    # ----------------------------------------------------------------------
    # Alert evaluation from a reading
    # ----------------------------------------------------------------------
    def evaluate_reading_alerts(
        self,
        reading: Reading,
        *,
        sensor_type: str,
        community_id: int,
        recipient_user_ids: Optional[list[int]] = None,
        user_id: Optional[int] = None,
    ):
        """
        Compatibility wrapper around AlertService.evaluate().

        Since Reading does not natively contain sensor_type/community_id/user routing,
        this method enriches it dynamically before delegating to AlertService.
        """
        if self.automation_rule_service:
            return self.automation_rule_service.evaluate_reading(
                reading,
                sensor_type=sensor_type,
                community_id=community_id,
                recipient_user_ids=recipient_user_ids,
                user_id=user_id,
            )

        enriched_reading = SimpleNamespace(
            id=getattr(reading, "id", None),
            sensor_id=getattr(reading, "sensor_id", None),
            timestamp=getattr(reading, "timestamp", None),
            value=getattr(reading, "value", None),
            unit=getattr(reading, "unit", None),
            sensor_type=sensor_type,
            community_id=community_id,
            recipient_user_ids=recipient_user_ids,
            user_id=user_id,
        )
        return self.alert_service.evaluate(enriched_reading)
