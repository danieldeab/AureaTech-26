# models.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: int
    email: str
    password_hash: str
    display_name: str

@dataclass
class Session:
    current_user: Optional[User] = None

    @property
    def is_authenticated(self) -> bool:
        return self.current_user is not None

    def clear(self):
        self.current_user = None
