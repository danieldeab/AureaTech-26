# app/service/monitoring_service.py

from __future__ import annotations
import threading
import time
import random
from datetime import datetime, timezone
from typing import Optional, Callable

from app.model.reading import Reading
from app.model.sensor import Sensor
from app.repository.sensor_repository import SensorRepository
from app.repository.reading_repository import ReadingRepository
from app.repository.alert_repository import AlertRepository
from app.repository.log_repository import LogRepository
from app.model.alert import Alert
from app.model.enums import SeverityEnum


class MonitoringService:
    """
    Global monitoring engine:
    - Monitors ALL sensors in the system
    - Generates readings
    - Triggers alerts
    - Writes logs
    - Runs in a background thread

    Community filtering happens in DashboardService & AlertService,
    NOT here (Option A).
    """

    def __init__(
        self,
        sensor_repo: SensorRepository,
        reading_repo: ReadingRepository,
        alert_repo: AlertRepository,
        log_repo: LogRepository,
        *,
        interval_seconds: int = 10,
    ):
        self.sensor_repo = sensor_repo
        self.reading_repo = reading_repo
        self.alert_repo = alert_repo
        self.log_repo = log_repo

        self.interval = interval_seconds
        self._thread: Optional[threading.Thread] = None
        self._running = False

    # ----------------------------------------------------------------------
    # PUBLIC API
    # ----------------------------------------------------------------------

    def start(self):
        """Starts the monitoring loop in the background."""
        if self._running:
            return  # already running

        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stops the monitoring thread safely."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)

    # ----------------------------------------------------------------------
    # MAIN LOOP
    # ----------------------------------------------------------------------

    def _run_loop(self):
        """Monitoring loop: runs every interval_seconds."""
        while self._running:
            try:
                self._process_once()
            except Exception as e:
                self._log_system_event(
                    event="monitoring_error",
                    description=f"Error in monitoring loop: {e}"
                )
            time.sleep(self.interval)

    # ----------------------------------------------------------------------
    # SINGLE MONITORING CYCLE
    # ----------------------------------------------------------------------

    def _process_once(self):
        """Process all sensors one time."""
        sensors = self.sensor_repo.get_all()

        for sensor in sensors:
            reading = self._simulate_reading(sensor)
            self._store_reading(sensor, reading)
            self._check_alert(sensor, reading)

    # ----------------------------------------------------------------------
    # READING GENERATION
    # (simple simulation, NOT the generate_readings.py historical batch generator)
    # ----------------------------------------------------------------------

    def _simulate_reading(self, sensor: Sensor) -> Reading:
        """
        Simple simulation logic for live monitoring.
        Uses thresholds if present, otherwise defaults.
        """

        sensor_type = sensor.type.lower()
        thresholds = sensor.thresholds or {}

        def _val(minv, maxv):
            return round(random.uniform(minv, maxv), 2)

        if sensor_type == "temperature":
            minv = thresholds.get("min", 10)
            maxv = thresholds.get("max", 40)
            unit = "°C"
            value = _val(minv, maxv)

        elif sensor_type == "humidity":
            minv = thresholds.get("min", 20)
            maxv = thresholds.get("max", 90)
            unit = "%"
            value = _val(minv, maxv)

        elif sensor_type == "light":
            minv = thresholds.get("min", 50)
            maxv = thresholds.get("max", 2000)
            unit = "lux"
            value = _val(minv, maxv)

        elif sensor_type == "air_quality":
            minv = thresholds.get("min", 0)
            maxv = thresholds.get("max", 500)
            unit = "aqi"
            value = _val(minv, maxv)

        elif sensor_type == "motion":
            unit = "bool"
            value = 1 if random.random() > 0.7 else 0

        else:
            minv = thresholds.get("min", 0)
            maxv = thresholds.get("max", 100)
            unit = "u"
            value = _val(minv, maxv)

        reading = Reading.new(
            sensor_id=sensor.id,
            value=value,
            unit=unit,
        )
        return reading

    # ----------------------------------------------------------------------
    # STORAGE
    # ----------------------------------------------------------------------

    def _store_reading(self, sensor: Sensor, reading: Reading):
        """Store reading in both sensor and reading repository."""
        sensor.readings.append(reading)
        self.sensor_repo.save(sensor)
        self.reading_repo.save(sensor.id, reading)

    # ----------------------------------------------------------------------
    # ALERT GENERATION
    # ----------------------------------------------------------------------

    def _check_alert(self, sensor: Sensor, reading: Reading):
        """
        Generates alerts according to simplified rules:
        - Temperature critical
        - Humidity extremes
        - Light too low
        - Bad air quality

        Alerts target the community's users:
        - Technicians & neighbors will see them based on DashboardService filtering
        """

        t = sensor.type.lower()
        v = reading.value

        alert: Optional[Alert] = None

        if t == "temperature" and v > 35:
            alert = Alert.new(
                type="high_temperature",
                severity=SeverityEnum.HIGH,
                message=f"Critical temperature detected: {v}°C",
                target_user_id=sensor.community_id,  # TEMPORARY (explained below)
            )
        elif t == "humidity" and v < 25:
            alert = Alert.new(
                type="low_humidity",
                severity=SeverityEnum.MEDIUM,
                message=f"Low humidity detected: {v}%",
                target_user_id=sensor.community_id,
            )
        elif t == "light" and v < 100:
            alert = Alert.new(
                type="low_light",
                severity=SeverityEnum.LOW,
                message=f"Low light detected: {v} lux",
                target_user_id=sensor.community_id,
            )
        elif t == "air_quality" and v > 200:
            alert = Alert.new(
                type="air_quality_bad",
                severity=SeverityEnum.HIGH,
                message=f"Poor air quality: {v} AQI",
                target_user_id=sensor.community_id,
            )

        if alert:
            self.alert_repo.add_alert(alert)
            self._log_system_event(
                event="alert_generated",
                description=alert.message,
                metadata={
                    "sensor_id": str(sensor.id),
                    "community_id": sensor.community_id,
                    "alert_type": alert.type,
                }
            )

    # ----------------------------------------------------------------------
    # LOGGING
    # ----------------------------------------------------------------------

    def _log_system_event(self, event: str, description: str, metadata: Optional[dict] = None):
        ts = int(time.time())
        entry = {
            "id": f"log-{ts}-{random.randint(1000,9999)}",
            "ts": ts,
            "event_type": event,
            "description": description,
            "metadata": metadata or {},
            "user_id": None,
        }
        self.log_repo.add(entry)
