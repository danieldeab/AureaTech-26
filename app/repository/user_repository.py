import json
import os
from app.model.models import User
from app.repository.interfaces.user_repository_interface import IUserRepository

USERS_PATH = os.path.join("data", "usuarios.json")

class UserRepository(IUserRepository):
    def __init__(self, path=USERS_PATH):
        self.path = path
        self.users = self._load()

    def _load(self):
        if not os.path.exists(self.path):
            return []

        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # data MUST be a list of dicts
        if isinstance(data, dict) and "usuarios" in data:
            data = data["usuarios"]

        # Convert legacy users to new schema if needed
        cleaned = []
        for u in data:
            if "fullname" not in u:
                # It's legacy style: convert it
                cleaned.append(self._convert_legacy_user(u))
            else:
                cleaned.append(User(**u))

        return cleaned

    def _convert_legacy_user(self, u):
        """
        Convert old format:
            id, email, password_hash, display_name, password
        to new format:
            fullname, email, password(hashed), dob, role
        """
        return User(
            fullname=u.get("display_name", "Usuario"),
            email=u.get("email"),
            password=u.get("password_hash"),   # we keep legacy hash
            dob="2000-01-01",                  # default (no dob in legacy)
            role="vecino"
        )

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([u.__dict__ for u in self.users], f, ensure_ascii=False, indent=4)

    def add_user(self, user: User):
        self.users.append(user)

    def find_by_email(self, email: str):
        for u in self.users:
            if u.email.lower() == email.lower():
                return u
        return None
    
    def get_all(self):
        return self.users
