from abc import ABC, abstractmethod
from typing import List, Optional


class ISoporteRepository(ABC):

    @abstractmethod
    def add_soporte(self, soporte) -> None:
        #Añade un centro de soporte a la colección en memoria
        pass

    @abstractmethod
    def find_by_id(self, soporte_id: str):
        #Encuentra un centro de soporte por ID o retorna None
        pass

    @abstractmethod
    def get_all(self) -> List:
        #Devuelve la lista completa de centros de soporte cargados
        pass
