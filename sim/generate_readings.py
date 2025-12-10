import argparse
import math
import random
from datetime import datetime, timedelta
from typing import Iterable, Tuple, Dict

from app.model.reading import Reading
from app.repository.sensor_repository import SensorRepository
from app.repository.reading_repository import ReadingRepository


class ReadingGenerator:
    """
    Genera lecturas simuladas para sensores de temperatura y humedad
    de una zona residencial en Madrid (interior, lejos del mar).

    """

    def __init__(self, sensors: SensorRepository | None = None, readings: ReadingRepository | None = None):
        self.sensor_repo = sensors or SensorRepository()
        self.reading_repo = readings or ReadingRepository()

    # -------- Modelos climáticos simplificados para Madrid --------
    @staticmethod
    def _seasonal_baseline(dt: datetime) -> Tuple[float, float]:
        """
        Devuelve (min_diario, max_diario) de temperatura (°C) para la fecha dada.
        Invierno más frío, verano más cálido. Aproximación por mes.
        """
        m = dt.month
        if m in (12, 1, 2):
            return (2.0, 14.0)  # Invierno
        if m in (3, 11):
            return (4.0, 16.0)  # Fines/inicios de frío
        if m in (4, 10):
            return (7.0, 20.0)  # Primavera/Otoño suave
        if m in (5, 9):
            return (12.0, 28.0)  # Templado cálido
        if m in (6, 8):
            return (17.0, 34.0)  # Verano fuerte
        # Julio
        return (19.0, 36.0)

    @staticmethod
    def _daily_temp(dt: datetime) -> float:
        """Temperatura horario con ciclo diario: mín ~06:00, máx ~16:00."""
        tmin, tmax = ReadingGenerator._seasonal_baseline(dt)
        amp = (tmax - tmin) / 2.0
        mid = (tmax + tmin) / 2.0
        # Fase: desplazar seno para que a las 16h esté cerca del máximo
        hour = dt.hour + dt.minute / 60.0
        # Convertimos hora a ángulo (24h -> 2π), con fase para pico ~16:00
        angle = 2 * math.pi * (hour - 16) / 24.0
        value = mid - amp * math.cos(angle)  # cos con fase para controlar pico
        # Ruido suave
        value += random.gauss(0, 0.6)
        # Límites absolutos razonables para Madrid
        return max(-8.0, min(42.0, value))

    @staticmethod
    def _daily_humidity(dt: datetime, temp_c: float) -> float:
        """Humedad relativa antiparalela a la temperatura; más alta por la noche."""
        hour = dt.hour + dt.minute / 60.0
        # Base nocturna más alta, diurna más baja
        # Usamos cos para que 6-8h sea relativamente alto y 15h bajo
        angle = 2 * math.pi * (hour - 5) / 24.0
        base = 50 - 15 * math.cos(angle)  # oscila aprox entre 35 y 65
        # Ajuste por temperatura (más calor -> menos humedad)
        base += -0.35 * (temp_c - 20.0)
        # Ruido
        val = base + random.gauss(0, 4.0)
        # Límites plausibles interior Madrid
        return max(15.0, min(95.0, val))

    def _calc_units(self) -> Dict[str, str]:
        return {"temperature": "C", "humidity": "%"}

    def generate(self, hours: int = 24, interval_min: int = 10, start: datetime | None = None) -> int:
        """
        Genera lecturas para los sensores de tipo temperature/humidity existentes.
        Devuelve el número de lecturas creadas.
        """
        sensors = [s for s in self.sensor_repo.get_all() if getattr(s, "type", None) in ("temperature", "humidity")]
        if not sensors:
            return 0

        units = self._calc_units()
        end = datetime.now() if start is None else start
        begin = end - timedelta(hours=hours)

        total_created = 0
        current = begin
        while current <= end:
            # Calcula una temperatura base para la hora; la humedad depende de ella
            temp_val = self._daily_temp(current)
            hum_val = self._daily_humidity(current, temp_val)

            for s in sensors:
                if s.type == "temperature":
                    r = Reading.new(sensor_id=s.id, value=float(temp_val), unit=units["temperature"], timestamp=current)
                    self.reading_repo.add_reading(r)
                    total_created += 1
                elif s.type == "humidity":
                    r = Reading.new(sensor_id=s.id, value=float(hum_val), unit=units["humidity"], timestamp=current)
                    self.reading_repo.add_reading(r)
                    total_created += 1

            current += timedelta(minutes=interval_min)

        self.reading_repo.save()
        return total_created


def main():
    parser = argparse.ArgumentParser(description="Genera lecturas sintéticas para sensores de temperatura y humedad (Madrid)")
    parser.add_argument("--hours", type=int, default=24, help="Horas hacia atrás a generar (default 24)")
    parser.add_argument("--interval-min", type=int, default=10, help="Minutos entre lecturas (default 10)")
    parser.add_argument("--end", type=str, default=None, help="Fin ISO8601 (por defecto ahora). Ej: 2025-12-10T10:00:00")
    args = parser.parse_args()

    end_dt = datetime.fromisoformat(args.end) if args.end else None

    gen = ReadingGenerator()
    n = gen.generate(hours=args.hours, interval_min=args.interval_min, start=end_dt)
    print(f"✔ Lecturas generadas: {n}")


if __name__ == "__main__":
    main()
