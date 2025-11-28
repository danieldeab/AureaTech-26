from abc import ABC, abstractmethod
from typing import Dict, List

class ILogRepository(ABC):

    @abstractmethod
    def add(self, entry: Dict):
        pass

    @abstractmethod
    def all(self) -> List[Dict]:
        pass
