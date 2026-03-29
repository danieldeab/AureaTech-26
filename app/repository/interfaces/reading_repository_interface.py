from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from app.model.reading import Reading


class IReadingRepository(ABC):

    @abstractmethod
    def add_reading(self, reading: Reading) -> None:
        pass

    @abstractmethod
    def find_by_sensor(self, sensor_id: UUID) -> List[Reading]:
        pass

    @abstractmethod
    def get_all(self) -> List[Reading]:
        pass
