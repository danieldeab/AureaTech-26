# app/model/user_repository.py

import json
import os

from app.model.models import User


USERS_PATH = os.path.join("data", "usuarios.json")


class UserRepository:
    def __init__(self):
        self.users = self._load()

    def _load(self):
        if not os.path.exists(USERS_PATH):
            return []
        with open(USERS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [User(**u) for u in data]

    def save(self):
        with open(USERS_PATH, "w", encoding="utf-8") as f:
            json.dump([u.__dict__ for u in self.users], f, ensure_ascii=False, indent=4)

    def add_user(self, user: User):
        self.users.append(user)

    def find_by_email(self, email: str):
        for u in self.users:
            if u.email.lower() == email.lower():
                return u
        return None
