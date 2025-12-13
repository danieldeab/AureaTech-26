import argparse
from typing import List
from random import randint, choice

from app.model.sensor import Sensor
from app.repository.sensor_repository import SensorRepository

class SensorGenerator:
    """
    Genera sensores de simulación para una zona residencial, reusando el dominio existente.

    """

    def __init__(self, repository: SensorRepository | None = None):
        self.repository = repository or SensorRepository()

    def _exists(self, type_: str, location: str, community_id: int) -> bool:
        for s in self.repository.get_all():
            if (
                getattr(s, "type", None) == type_
                and (getattr(s, "location", None) == location)
                and (getattr(s, "community_id", None) == community_id)
            ):
                return True
        return False

    def generate_default_residential(
            self, 
            location: str = "Zona Residencial",
            community_id: int = 1,
            include_optionals: bool = True
    ) -> List[Sensor]:
        
        created: List[Sensor] = []

        temp_thresholds = {"min": -5.0, "max": 42.0}
        hum_thresholds = {"min": 20.0, "max": 85.0}
        light_thresholds = {"min": 0.0, "max": 1000.0}      # Lux (LDR)
        distance_thresholds = {"min": 2.0, "max": 450.0}   # cm (HC-SR04)
        smoke_thresholds = {"min": 0.0, "max": 300.0}      # ppm (simulated)
        wind_thresholds = {"min": 0.0, "max": 150.0}       # km/h

        # ---- Mandatory sensors ----
        def add(type_, thresholds=None):
            if not self._exists(type_, location, community_id):
                s = Sensor.new(
                    type=type_,
                    location=location,
                    community_id=community_id,
                    thresholds=thresholds
                )
                self.repository.add_sensor(s)
                created.append(s)

        add("temperature", temp_thresholds)
        add("humidity", hum_thresholds)
        add("luminosity", light_thresholds)
        add("distance", distance_thresholds)

        # ---- Optional sensors ----
        if include_optionals:
            add("smoke", smoke_thresholds)        # Fire detection
            add("wind", wind_thresholds)          # Anemometer
            add("camera", thresholds=None)        # License plate source

        if created:
            self.repository.save()
        return created

def main():
    parser = argparse.ArgumentParser(description="Genera sensores (temperatura, humedad, luminosidad, distancia, humo, viento, cámara) para simulación")
    parser.add_argument(
        "--location", 
        default="Zona Residencial",
        help="Ubicación/estancia de los sensores"
    )
    parser.add_argument(
        "--no-optionals",
        action="store_true",
        help="No generar sensores opcionales"
    )
    args = parser.parse_args()

    repo = SensorRepository()
    gen = SensorGenerator(repo)
    
    for cid in (1, 2):
        created = gen.generate_default_residential(
            location=args.location,
            community_id=cid,
            include_optionals=not args.no_optionals
        )

        if created:
            print(
                f"Sensores creados para comunidad {cid}: "
                + ", ".join(f"{s.type}@{s.location}" for s in created)
            )
        else:
            print(
                f"No se crearon sensores para comunidad {cid}: "
                "ya existían todos."
            )



if __name__ == "__main__":
    main()
