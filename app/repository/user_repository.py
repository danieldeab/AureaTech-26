import json
import os
from app.model.user import User
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

        # Load using the domain factory
        loaded = []
        for u in data:
            try:
                loaded.append(User.from_dict(u))
            except Exception as e:
                print(f"[UserRepository] Error loading user: {e}\nUser data: {u}")
        return loaded
    
    def save(self):
        tmp_path = self.path + ".tmp"

        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump([u.to_dict() for u in self.users], f, ensure_ascii=False, indent=4)

        os.replace(tmp_path, self.path)

    def add_user(self, user: User):
        self.users.append(user)

    def find_by_email(self, email: str):
        email = email.strip().lower()
        for u in self.users:
            if u.email.lower() == email:
                return u
        return None
    
    def get_all(self):
        return self.users
