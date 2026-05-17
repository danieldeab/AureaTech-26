from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from app.repository.plate_repository import normalize_plate


class VisionPlateService:
    """
    Application boundary for camera/model input.

    The current YOLO recognizer detects plate regions. If the recognizer or the
    caller also provides plate text, this service records the detection through
    PlateRecognitionService so the normal DB/audit/alert workflow runs.
    """

    def __init__(self, *, plate_recognition_service, recognizer=None, error_service=None):
        self.plate_recognition_service = plate_recognition_service
        self.recognizer = recognizer
        self.error_service = error_service

    def process_image(
        self,
        *,
        sensor_id: int,
        image_path: str,
        detected_plate: str | None = None,
        detected_at: datetime | None = None,
        save_result: bool = True,
    ) -> dict[str, Any]:
        try:
            path = Path(image_path)
            if not path.exists():
                raise ValueError(f"Image not found: {image_path}")

            detections = []
            if self.recognizer:
                detections = self.recognizer.detect(str(path), save_result=save_result)

            plate = normalize_plate(detected_plate or self._extract_plate_text(detections) or "")
            if not plate:
                return {
                    "recorded": False,
                    "reason": "plate_text_not_available",
                    "sensor_id": int(sensor_id),
                    "image_path": str(path),
                    "detections": detections,
                }

            event = self.plate_recognition_service.record_detection(
                sensor_id=int(sensor_id),
                detected_plate=plate,
                detected_at=detected_at,
                image_path=str(path),
            )
            return {
                "recorded": True,
                "event": event,
                "detections": detections,
            }
        except Exception as exc:
            if self.error_service:
                self.error_service.capture_exception(
                    exc,
                    severity="ERROR",
                    source_layer="VISION",
                    target_entity_type="camera_event",
                    target_entity_id=int(sensor_id),
                )
            raise

    def process_plate_text(
        self,
        *,
        sensor_id: int,
        detected_plate: str,
        image_path: str | None = None,
        detected_at: datetime | None = None,
    ) -> dict[str, Any]:
        event = self.plate_recognition_service.record_detection(
            sensor_id=int(sensor_id),
            detected_plate=normalize_plate(detected_plate),
            detected_at=detected_at,
            image_path=image_path,
        )
        return {"recorded": True, "event": event, "detections": []}

    def _extract_plate_text(self, detections: list[dict[str, Any]]) -> str | None:
        text_keys = ("detected_plate", "plate", "plate_text", "text", "license_plate")
        for detection in detections:
            for key in text_keys:
                value = detection.get(key)
                if value:
                    return str(value)
        return None
