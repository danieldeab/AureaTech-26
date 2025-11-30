# app/model/models.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    fullname: str
    email: str
    password: str      # already hashed
    dob: str
    role: str = "vecino"
    picture_path: Optional[str] = None


@dataclass
class Session:
    current_user: Optional[User] = None

    @property
    def is_authenticated(self) -> bool:
        return self.current_user is not None

    def clear(self):
        self.current_user = None

    def get_current_user(self):
        return self.current_user
    
    def set_current_user(self, user: User):
        self.current_user = user
