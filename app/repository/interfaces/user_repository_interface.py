from abc import ABC, abstractmethod
from app.model.user import User
from typing import Optional, List

class IUserRepository(ABC):

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def find_by_community_id(self, community_id: int) -> List[User]:
        pass

    @abstractmethod
    def add_user(self, user: User):
        pass

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def get_all(self) -> List[User]:
        pass
