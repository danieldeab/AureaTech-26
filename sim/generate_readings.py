import argparse
import math
import random
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.infraestructure.db import get_db
from app.model.reading import Reading
from app.repository.reading_repository import ReadingRepository
from app.repository.sensor_repository import SensorRepository


class ReadingGenerator:
    """
    Generate synthetic readings matching current DB constraints:
    - reading.reading_value is DECIMAL(10,2) -> numeric only
    - unit is VARCHAR(20) NOT NULL
    - camera detections go to camera_event (not reading table)
    """

    def __init__(
        self,
        sensors: SensorRepository | None = None,
        readings: ReadingRepository | None = None,
    ):
        self.sensor_repo = sensors or SensorRepository()
        self.reading_repo = readings or ReadingRepository()
        self.db = get_db()

    @staticmethod
    def _seasonal_baseline(dt: datetime) -> Tuple[float, float]:
        month = dt.month
        if month in (12, 1, 2):
            return 2.0, 14.0
        if month in (3, 11):
            return 4.0, 16.0
        if month in (4, 10):
            return 7.0, 20.0
        if month in (5, 9):
            return 12.0, 28.0
        if month in (6, 8):
            return 17.0, 34.0
        return 19.0, 36.0

    @staticmethod
    def _daily_temp(dt: datetime) -> float:
        tmin, tmax = ReadingGenerator._seasonal_baseline(dt)
        amp = (tmax - tmin) / 2.0
        mid = (tmax + tmin) / 2.0
        hour = dt.hour + dt.minute / 60.0
        angle = 2 * math.pi * (hour - 16) / 24.0
        value = mid - amp * math.cos(angle) + random.gauss(0, 0.6)
        return max(-8.0, min(42.0, value))

    @staticmethod
    def _daily_humidity(dt: datetime, temp_c: float) -> float:
        hour = dt.hour + dt.minute / 60.0
        angle = 2 * math.pi * (hour - 5) / 24.0
        base = 50 - 15 * math.cos(angle)
        base += -0.35 * (temp_c - 20.0)
        return max(15.0, min(95.0, base + random.gauss(0, 4.0)))

    @staticmethod
    def _daily_lux(dt: datetime) -> float:
        hour = dt.hour + dt.minute / 60.0
        if hour < 6 or hour > 20:
            return random.uniform(0, 5)
        angle = math.pi * (hour - 6) / 14.0
        return max(0.0, 1000.0 * math.sin(angle) + random.gauss(0, 30))

    @staticmethod
    def _distance_cm() -> float:
        return random.uniform(20, 120) if random.random() < 0.15 else random.uniform(200, 450)

    @staticmethod
    def _smoke_ppm() -> float:
        return random.uniform(120, 300) if random.random() < 0.01 else random.uniform(0, 40)

    @staticmethod
    def _wind_kmh() -> float:
        return max(0.0, min(120.0, random.gauss(10, 6)))

    @staticmethod
    def _units() -> Dict[str, str]:
        return {
            "TEMPERATURE": "C",
            "HUMIDITY": "%",
            "LIGHT": "lux",
            "DISTANCE": "cm",
            "SMOKE": "ppm",
            "WIND": "km/h",
        }

    @staticmethod
    def _generate_license_plate() -> str:
        digits = f"{random.randint(0, 9999):04d}"
        letters = "".join(random.choice("BCDFGHJKLMNPRSTVWXYZ") for _ in range(3))
        return f"{digits} {letters}"

    def _insert_camera_event(self, sensor_id: int, ts: datetime) -> None:
        plate = self._generate_license_plate()
        self.db.insert(
            table="camera_event",
            data={
                "sensor_id": int(sensor_id),
                "detected_plate": plate,
                "is_allowed": 1 if random.random() < 0.7 else 0,
                "detected_at": ts,
                "image_path": None,
            },
        )

    def _sensor_value(self, sensor_type: str, ts: datetime, temp_cache: float, hum_cache: float) -> Optional[float]:
        st = sensor_type.upper()
        if st == "TEMPERATURE":
            return temp_cache
        if st == "HUMIDITY":
            return hum_cache
        if st == "LIGHT":
            return self._daily_lux(ts)
        if st == "DISTANCE":
            return self._distance_cm()
        if st == "SMOKE":
            return self._smoke_ppm()
        if st == "WIND":
            return self._wind_kmh()
        return None

    def generate(self, hours: int = 24, interval_min: int = 10, end: datetime | None = None) -> int:
        sensors = [s for s in self.sensor_repo.get_all() if bool(getattr(s, "is_enabled", False))]
        if not sensors:
            return 0

        end_dt = end or datetime.now()
        begin_dt = end_dt - timedelta(hours=hours)
        units = self._units()
        total_created = 0
        current = begin_dt

        while current <= end_dt:
            temp_val = self._daily_temp(current)
            hum_val = self._daily_humidity(current, temp_val)

            for sensor in sensors:
                sensor_id = getattr(sensor, "sensor_id", None)
                sensor_type = str(getattr(sensor, "type", "")).upper()
                if sensor_id is None or not sensor_type:
                    continue

                if sensor_type == "CAMERA":
                    if random.random() < 0.05:
                        self._insert_camera_event(int(sensor_id), current)
                        total_created += 1
                    continue

                value = self._sensor_value(sensor_type, current, temp_val, hum_val)
                unit = units.get(sensor_type)
                if value is None or not unit:
                    continue

                reading = Reading(
                    id=None,  # type: ignore[arg-type]
                    sensor_id=int(sensor_id),  # type: ignore[arg-type]
                    timestamp=current,
                    value=round(float(value), 2),
                    unit=unit,
                )
                self.reading_repo.add_reading(reading)
                total_created += 1

            current += timedelta(minutes=interval_min)

        return total_created


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic readings matching DB constraints")
    parser.add_argument("--hours", type=int, default=24)
    parser.add_argument("--interval-min", type=int, default=10)
    parser.add_argument("--end", type=str, default=None, help="ISO datetime, e.g. 2026-05-16T12:00:00")
    args = parser.parse_args()

    end_dt = datetime.fromisoformat(args.end) if args.end else None
    created = ReadingGenerator().generate(hours=args.hours, interval_min=args.interval_min, end=end_dt)
    print(f"Readings/events generated: {created}")


if __name__ == "__main__":
    main()
