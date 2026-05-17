from __future__ import annotations

import threading
import time
from typing import Callable, Optional

from app.service.dashboard_event_bus import DashboardEventBus


class SensorIngestionWorker:
    def __init__(
        self,
        reading_service,
        event_bus: DashboardEventBus,
        payload_provider: Callable[[], Optional[dict]],
        *,
        interval_seconds: float = 1.0,
        error_service=None,
    ):
        self.reading_service = reading_service
        self.event_bus = event_bus
        self.payload_provider = payload_provider
        self.interval_seconds = max(0.05, float(interval_seconds))
        self.error_service = error_service
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="SensorIngestionWorker")
        self._thread.start()

    def stop(self, timeout: float = 2.0) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=timeout)

    def _run(self) -> None:
        while not self._stop_event.is_set():
            payload = self.payload_provider()
            if payload:
                self._process_payload(payload)
            self._stop_event.wait(self.interval_seconds)

    def _process_payload(self, payload: dict) -> None:
        sensor_id = payload.get("sensor_id")
        value = payload.get("value")
        if sensor_id is None or value is None:
            self.event_bus.publish(
                {
                    "event_type": "ingestion_error",
                    "reason": "invalid_payload",
                    "payload": payload,
                }
            )
            self._capture_error(ValueError("Invalid sensor payload"), payload)
            return

        try:
            reading = self.reading_service.record_reading(
                sensor_id=int(sensor_id),
                value=value,
                unit=payload.get("unit"),
                recorded_at=payload.get("recorded_at"),
                raw_payload=payload.get("raw_payload"),
                recipient_user_ids=payload.get("recipient_user_ids"),
                user_id=payload.get("user_id"),
            )
            self.event_bus.publish(
                {
                    "event_type": "reading_recorded",
                    "sensor_id": int(sensor_id),
                    "value": reading.value,
                    "unit": reading.unit,
                    "timestamp": reading.timestamp.isoformat(),
                }
            )
        except Exception as exc:
            self.event_bus.publish(
                {
                    "event_type": "ingestion_error",
                    "reason": exc.__class__.__name__,
                    "message": str(exc),
                    "payload": payload,
                }
            )
            self._capture_error(exc, payload)

    def _capture_error(self, exc: Exception, payload: dict) -> None:
        if not self.error_service:
            return
        try:
            self.error_service.capture_exception(
                exc,
                severity="WARN",
                source_layer="INGESTION",
                user_id=payload.get("user_id"),
                target_entity_type="sensor",
                target_entity_id=int(payload["sensor_id"]) if payload.get("sensor_id") is not None else None,
            )
        except Exception:
            pass
