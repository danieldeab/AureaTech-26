import argparse
from typing import List

from app.model.sensor import Sensor
from app.repository.sensor_repository import SensorRepository


class SensorGenerator:
    """
    Genera sensores de simulación para una zona residencial, reusando el dominio existente.

    """

    def __init__(self, repository: SensorRepository | None = None):
        self.repository = repository or SensorRepository()

    def _exists(self, type_: str, location: str) -> bool:
        for s in self.repository.get_all():
            if getattr(s, "type", None) == type_ and getattr(s, "location", None) == location:
                return True
        return False

    def generate_default_residential(self, location: str = "Zona Residencial") -> List[Sensor]:
        created: List[Sensor] = []

        # Umbrales plausibles para Madrid (interior, lejos del mar)
        temp_thresholds = {"min": -5.0, "max": 42.0}
        hum_thresholds = {"min": 20.0, "max": 85.0}

        # Sensor de temperatura
        if not self._exists("temperature", location):
            temp = Sensor.new(type="temperature", location=location, thresholds=temp_thresholds)
            self.repository.add_sensor(temp)
            created.append(temp)

        # Sensor de humedad
        if not self._exists("humidity", location):
            hum = Sensor.new(type="humidity", location=location, thresholds=hum_thresholds)
            self.repository.add_sensor(hum)
            created.append(hum)

        if created:
            self.repository.save()
        return created


def main():
    parser = argparse.ArgumentParser(description="Genera sensores (temperatura y humedad) para simulación")
    parser.add_argument("--location", default="Zona Residencial", help="Ubicación/estancia de los sensores")
    args = parser.parse_args()

    repo = SensorRepository()
    gen = SensorGenerator(repo)
    created = gen.generate_default_residential(location=args.location)
    if created:
        print(f"✔ Sensores creados: {', '.join(f'{s.type}@{s.location}' for s in created)}")
    else:
        print("ℹ No se crearon sensores: ya existían temperatura y humedad en esa localización.")


if __name__ == "__main__":
    main()
