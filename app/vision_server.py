from __future__ import annotations

import argparse

from app.repository.alert_repository import AlertRepository
from app.repository.actuator_repository import ActuatorRepository
from app.repository.log_repository import LogRepository
from app.repository.plate_repository import PlateRepository
from app.repository.user_repository import UserRepository
from app.service.actuator_service import ActuatorService
from app.service.alert_service import AlertService
from app.service.audit_log_service import AuditLogService
from app.service.error_service import ErrorService
from app.service.plate_recognition_service import PlateRecognitionService
from app.service.vision_http_server import VisionHttpServer
from app.service.vision_plate_service import VisionPlateService


def build_vision_service(*, with_model: bool = False) -> VisionPlateService:
    log_repo = LogRepository()
    audit = AuditLogService(log_repo)
    errors = ErrorService()
    users = UserRepository()
    alerts = AlertService(AlertRepository())
    actuators = ActuatorService(ActuatorRepository(), audit_log_service=audit, error_service=errors)
    plates = PlateRepository()
    plate_service = PlateRecognitionService(
        plates,
        audit_log_service=audit,
        error_service=errors,
        actuator_service=actuators,
        alert_service=alerts,
        user_repository=users,
    )

    recognizer = None
    if with_model:
        from app.infraestructure.vision.plate_recognizer import PlateRecognizer

        recognizer = PlateRecognizer()

    return VisionPlateService(
        plate_recognition_service=plate_service,
        recognizer=recognizer,
        error_service=errors,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="AureaTech local vision ingestion endpoint")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument(
        "--with-model",
        action="store_true",
        help="Load the local YOLO model so image_path payloads can be processed directly.",
    )
    args = parser.parse_args()

    server = VisionHttpServer(
        build_vision_service(with_model=args.with_model),
        host=args.host,
        port=args.port,
    )
    print(f"Vision endpoint listening on http://{args.host}:{args.port}/plate-detections")
    server.start()


if __name__ == "__main__":
    main()
