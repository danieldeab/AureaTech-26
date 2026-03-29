from abc import ABC, abstractmethod
from typing import List, Optional
from app.model.sensor import Sensor


class ISensorRepository(ABC):

    @abstractmethod
    def add_sensor(self, sensor: Sensor) -> None:
        pass

    @abstractmethod
    def find_by_id(self, sensor_id: str) -> Optional[Sensor]:
        pass

    @abstractmethod
    def get_all(self) -> List[Sensor]:
        pass

    @abstractmethod
    def save(self) -> None:
        pass