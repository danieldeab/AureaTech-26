from __future__ import annotations

from datetime import datetime
from typing import Any

from app.model.enums import RoleEnum
from app.model.enums import SeverityEnum
from app.repository.plate_repository import PlateRepository, normalize_plate
from app.service.audit_log_service import AuditLogService
from app.service.error_service import ErrorService


class PlateRecognitionService:
    def __init__(
        self,
        plate_repository: PlateRepository,
        *,
        audit_log_service: AuditLogService | None = None,
        error_service: ErrorService | None = None,
        actuator_service=None,
        alert_service=None,
        user_repository=None,
    ):
        self.plate_repository = plate_repository
        self.audit_log_service = audit_log_service or AuditLogService()
        self.error_service = error_service or ErrorService()
        self.actuator_service = actuator_service
        self.alert_service = alert_service
        self.user_repository = user_repository

    def record_detection(
        self,
        *,
        sensor_id: int,
        detected_plate: str,
        detected_at: datetime | None = None,
        image_path: str | None = None,
        actor_id: int = 1,
    ) -> dict[str, Any]:
        try:
            plate = normalize_plate(detected_plate)
            if not plate:
                raise ValueError("Detected plate cannot be empty.")

            community_id = self.plate_repository.get_sensor_community_id(int(sensor_id))
            if community_id is None:
                raise ValueError(f"Sensor {sensor_id} not found.")

            allowed = self.plate_repository.find_allowed_plate(plate, community_id)
            is_allowed = allowed is not None
            event_id = self.plate_repository.add_camera_event(
                sensor_id=int(sensor_id),
                detected_plate=plate,
                is_allowed=is_allowed,
                detected_at=detected_at or datetime.now(),
                image_path=image_path,
            )

            self.audit_log_service.log(
                actor_id=int(actor_id),
                actor_role=RoleEnum.ADMIN,
                category="CAMERA",
                action="plate_detected",
                details=f"Plate {plate} allowed={is_allowed}",
                community_id=int(community_id),
                target_entity_type="camera_event",
                target_entity_id=int(event_id),
            )

            alert_result = None
            if not is_allowed:
                alert_result = self._notify_technicians(
                    community_id=int(community_id),
                    plate=plate,
                    camera_event_id=int(event_id),
                )

            return {
                "camera_event_id": int(event_id),
                "sensor_id": int(sensor_id),
                "community_id": int(community_id),
                "detected_plate": plate,
                "is_allowed": is_allowed,
                "allowed_plate": allowed,
                "alert_result": alert_result,
            }
        except Exception as exc:
            self.error_service.capture_exception(
                exc,
                source_layer="SERVICE",
                community_id=None,
                target_entity_type="camera_event",
            )
            raise

    def list_user_plates(self, user_id: int) -> list[dict[str, Any]]:
        return self.plate_repository.list_user_plates(int(user_id))

    def list_pending_plates(self, community_id: int | None = None) -> list[dict[str, Any]]:
        return self.plate_repository.list_pending_plates(community_id)

    def request_user_plate(self, *, user_id: int, community_id: int, plate: str) -> int:
        normalized = normalize_plate(plate)
        if not normalized:
            raise ValueError("Plate cannot be empty.")
        new_id = self.plate_repository.request_plate(
            user_id=int(user_id),
            community_id=int(community_id),
            plate=normalized,
        )
        self.audit_log_service.log(
            actor_id=int(user_id),
            actor_role=RoleEnum.NEIGHBOR,
            category="PLATE",
            action="plate_requested",
            details=f"Plate {normalized} requested",
            community_id=int(community_id),
            target_entity_type="allowed_plate",
            target_entity_id=int(new_id),
        )
        return int(new_id)

    def approve_plate(self, *, allowed_plate_id: int, actor_id: int, actor_role: RoleEnum, community_id: int | None = None) -> None:
        if actor_role != RoleEnum.ADMIN:
            raise PermissionError("Only admins can approve plates.")
        self.plate_repository.approve_plate(int(allowed_plate_id))
        self.audit_log_service.log(
            actor_id=int(actor_id),
            actor_role=actor_role,
            category="PLATE",
            action="plate_approved",
            details=f"Plate request {allowed_plate_id} approved",
            community_id=community_id,
            target_entity_type="allowed_plate",
            target_entity_id=int(allowed_plate_id),
        )

    def deny_plate(self, *, allowed_plate_id: int, actor_id: int, actor_role: RoleEnum, community_id: int | None = None) -> None:
        if actor_role != RoleEnum.ADMIN:
            raise PermissionError("Only admins can deny plates.")
        self.plate_repository.delete_plate(int(allowed_plate_id))
        self.audit_log_service.log(
            actor_id=int(actor_id),
            actor_role=actor_role,
            category="PLATE",
            action="plate_denied",
            details=f"Plate request {allowed_plate_id} denied",
            community_id=community_id,
            target_entity_type="allowed_plate",
            target_entity_id=int(allowed_plate_id),
        )

    def deactivate_user_plate(self, *, allowed_plate_id: int, user_id: int, community_id: int) -> None:
        self.plate_repository.deactivate_plate(int(allowed_plate_id), user_id=int(user_id))
        self.audit_log_service.log(
            actor_id=int(user_id),
            actor_role=RoleEnum.NEIGHBOR,
            category="PLATE",
            action="plate_deactivated",
            details=f"Plate {allowed_plate_id} deactivated by owner",
            community_id=int(community_id),
            target_entity_type="allowed_plate",
            target_entity_id=int(allowed_plate_id),
        )

    def _notify_technicians(self, *, community_id: int, plate: str, camera_event_id: int):
        if not self.alert_service or not self.user_repository:
            return None

        finder = getattr(self.user_repository, "find_by_community_id_and_role", None)
        if not callable(finder):
            return None

        technicians = finder(int(community_id), RoleEnum.TECHNICIAN.value)
        technician_ids = [int(t.id) for t in technicians if getattr(t, "id", None) is not None]
        if not technician_ids:
            return None

        return self.alert_service.create_and_deliver_alert(
            community_id=int(community_id),
            recipients=technician_ids,
            alert_type="unauthorized_plate",
            severity=SeverityEnum.WARN,
            message=f"Unauthorized plate detected: {plate}",
            rule_alert_action_id=1,
        )
