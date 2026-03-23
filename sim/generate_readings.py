import argparse
import math
import random
from datetime import datetime, timezone, timedelta
from typing import Iterable, Tuple, Dict

from app.model.reading import Reading
from app.repository.sensor_repository import SensorRepository
from app.repository.reading_repository import ReadingRepository


class ReadingGenerator:
    """
    Genera lecturas simuladas para sensores residenciales,
    incluyendo sensores obligatorios y opcionales.
    """

    def __init__(
        self,
        sensors: SensorRepository | None = None,
        readings: ReadingRepository | None = None
    ):
        self.sensor_repo = sensors or SensorRepository()
        self.reading_repo = readings or ReadingRepository()

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    @staticmethod
    def _seasonal_baseline(dt: datetime) -> Tuple[float, float]:
        m = dt.month
        if m in (12, 1, 2):
            return (2.0, 14.0)
        if m in (3, 11):
            return (4.0, 16.0)
        if m in (4, 10):
            return (7.0, 20.0)
        if m in (5, 9):
            return (12.0, 28.0)
        if m in (6, 8):
            return (17.0, 34.0)
        return (19.0, 36.0)

    @staticmethod
    def _daily_temp(dt: datetime) -> float:
        tmin, tmax = ReadingGenerator._seasonal_baseline(dt)
        amp = (tmax - tmin) / 2.0
        mid = (tmax + tmin) / 2.0
        hour = dt.hour + dt.minute / 60.0
        angle = 2 * math.pi * (hour - 16) / 24.0
        value = mid - amp * math.cos(angle)
        value += random.gauss(0, 0.6)
        return max(-8.0, min(42.0, value))

    @staticmethod
    def _daily_humidity(dt: datetime, temp_c: float) -> float:
        hour = dt.hour + dt.minute / 60.0
        angle = 2 * math.pi * (hour - 5) / 24.0
        base = 50 - 15 * math.cos(angle)
        base += -0.35 * (temp_c - 20.0)
        val = base + random.gauss(0, 4.0)
        return max(15.0, min(95.0, val))

    @staticmethod
    def _daily_luminosity(dt: datetime) -> float:
        """Lux curve: 0 at night, peak at midday."""
        hour = dt.hour + dt.minute / 60.0
        if hour < 6 or hour > 20:
            return random.uniform(0, 5)
        angle = math.pi * (hour - 6) / 14.0
        return max(0.0, 1000.0 * math.sin(angle) + random.gauss(0, 30))

    @staticmethod
    def _distance_value() -> float:
        """Simulate proximity events (people/cars passing)."""
        if random.random() < 0.15:
            return random.uniform(20, 120)   # object detected
        return random.uniform(200, 450)     # no object nearby

    @staticmethod
    def _smoke_value() -> float:
        """Mostly low values, rare spikes."""
        if random.random() < 0.01:
            return random.uniform(120, 300)
        return random.uniform(0, 40)

    @staticmethod
    def _wind_value() -> float:
        """Madrid-like wind distribution."""
        base = random.gauss(10, 6)
        return max(0.0, min(120.0, base))

    @staticmethod
    def _units() -> Dict[str, str]:
        return {
            "temperature": "C",
            "humidity": "%",
            "luminosity": "lux",
            "distance": "cm",
            "smoke": "ppm",
            "wind": "km/h",
            "camera": "plate",
        }

    @staticmethod
    def _generate_license_plate() -> str:
        digits = f"{random.randint(0, 9999):04d}"
        allowed_letters = "BCDFGHJKLMNPRSTVWXYZ"
        letters = "".join(random.choice(allowed_letters) for _ in range(3))
        return f"{digits} {letters}"

    @staticmethod
    def _random_timestamps(
        start: datetime,
        end: datetime,
        count: int
    ) -> list[datetime]:
        delta = int((end - start).total_seconds())
        return sorted(
            start + timedelta(seconds=random.randint(0, delta))
            for _ in range(count)
        )


    # --------------------------------------------------
    # Main generator
    # --------------------------------------------------

    def generate(
        self,
        hours: int = 24,
        interval_min: int = 10,
        start: datetime | None = None
    ) -> int:
        sensors = self.sensor_repo.get_all()
        if not sensors:
            return 0

        units = self._units()
        end = datetime.now() if start is None else start
        begin = end - timedelta(hours=hours)

        total_created = 0
        current = begin

        while current <= end:
            temp_val = self._daily_temp(current)
            hum_val = self._daily_humidity(current, temp_val)

            for s in sensors:
                value = None

                if s.type == "temperature":
                    value = temp_val
                elif s.type == "humidity":
                    value = hum_val
                elif s.type == "luminosity":
                    value = self._daily_luminosity(current)
                elif s.type == "distance":
                    value = self._distance_value()
                elif s.type == "smoke":
                    value = self._smoke_value()
                elif s.type == "wind":
                    value = self._wind_value()
                elif s.type == "camera":
                    # Rare events → cars do not pass every interval
                    if random.random() < 0.05:
                        value = self._generate_license_plate()
                    else:
                        continue  # no reading if nothing passes

                if value is not None:
                    r = Reading.new(
                        sensor_id=s.id,
                        value=value,
                        unit=units.get(s.type),
                        timestamp=current
                    )
                    self.reading_repo.add_reading(r)
                    total_created += 1

            current += timedelta(minutes=interval_min)

        self.reading_repo.save()
        return total_created

    def generate_random_in_window(
        self,
        days_back: int = 7,
        readings_per_sensor: int = 200
    ) -> int:
        """
        Genera lecturas en momentos aleatorios dentro de una ventana pasada.
        Ejemplos:
        - last week (days_back=7)
        - last month (days_back=30)
        """

        sensors = self.sensor_repo.get_all()
        if not sensors:
            return 0

        units = self._units()
        end = datetime.now()
        start = end - timedelta(days=days_back)

        total_created = 0

        timestamps = self._random_timestamps(
            start=start,
            end=end,
            count=readings_per_sensor
        )

        for ts in timestamps:
            temp_val = self._daily_temp(ts)
            hum_val = self._daily_humidity(ts, temp_val)

            for s in sensors:
                value = None

                if s.type == "temperature":
                    value = temp_val
                elif s.type == "humidity":
                    value = hum_val
                elif s.type == "luminosity":
                    value = self._daily_luminosity(ts)
                elif s.type == "distance":
                    value = self._distance_value()
                elif s.type == "smoke":
                    value = self._smoke_value()
                elif s.type == "wind":
                    value = self._wind_value()
                elif s.type == "camera":
                    if random.random() < 0.05:
                        value = self._generate_license_plate()
                    else:
                        continue

                if value is not None:
                    r = Reading.new(
                        sensor_id=s.id,
                        value=value,
                        unit=units.get(s.type),
                        timestamp=ts
                    )
                    self.reading_repo.add_reading(r)
                    total_created += 1

        self.reading_repo.save()
        return total_created


def main():
    parser = argparse.ArgumentParser(
        description="Genera lecturas sintéticas para sensores residenciales"
    )
    parser.add_argument("--hours", type=int, default=24)
    parser.add_argument("--interval-min", type=int, default=10)
    parser.add_argument("--end", type=str, default=None)
    parser.add_argument("--random-last-week", action="store_true")
    parser.add_argument("--random-last-month", action="store_true")

    args = parser.parse_args()

    end_dt = datetime.fromisoformat(args.end) if args.end else None

    gen = ReadingGenerator()

    if args.random_last_week:
        n = gen.generate_random_in_window(days_back=7)
    elif args.random_last_month:
        n = gen.generate_random_in_window(days_back=30)
    else:
        n = gen.generate(
            hours=args.hours,
            interval_min=args.interval_min,
            start=end_dt
        )
    print(f"✔ Lecturas generadas: {n}")


if __name__ == "__main__":
    main()
