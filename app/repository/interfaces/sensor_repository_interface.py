from abc import ABC, abstractmethod
from typing import List, Optional
from app.model.sensor import Sensor


class ISensorRepository(ABC):

    @abstractmethod
    def add_sensor(self, sensor: Sensor) -> None:
        #Añade un sensor a la colección en memoria
        pass

    @abstractmethod
    def find_by_id(self, sensor_id: str) -> Optional[Sensor]:
        #Encuentra un sensor por ID o retorna None
        pass

    @abstractmethod
    def get_all(self) -> List[Sensor]:
        #Devuelve la lista completa de sensores cargados
        pass
