from abc import ABC, abstractmethod
from typing import Dict, List, Any

class ILogRepository(ABC):

    @abstractmethod
    def add(self, entry: Dict):
        pass

    @abstractmethod
    def all(self) -> List[Dict]:
        pass

    @abstractmethod
    def search(
        self,
        filters: Dict[str, Any] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> List[Dict]:
        pass
