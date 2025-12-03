# app/model/models.py

from dataclasses import dataclass
from app.model.user import User
from typing import Optional

@dataclass
class Session:
    current_user: Optional[User] = None
    reset_email: Optional[str] = None

    @property
    def is_authenticated(self) -> bool:
        return self.current_user is not None

    def clear(self):
        self.current_user = None
        self.reset_email = None

    def get_current_user(self):
        return self.current_user
    
    def set_current_user(self, user: User):
        self.current_user = user

    def start_reset(self, email: str):
        self.reset_email = email

    def clear_reset(self):
        self.reset_email = None

    def logout(self):
        self.current_user = None
