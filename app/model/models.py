# app/models/models.py
# this one should get deprecated

from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: int
    email: str
    password_hash: str
    display_name: str
    # Campo opcional SOLO para desarrollo / debug
    password: Optional[str] = None

@dataclass
class Session:
    current_user: Optional[User] = None

    @property
    def is_authenticated(self) -> bool:
        return self.current_user is not None

    def clear(self):
        self.current_user = None
