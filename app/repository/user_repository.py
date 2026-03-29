import json
import os
from app.model.user import User
from app.repository.interfaces.user_repository_interface import IUserRepository

# Always resolve data path relative to the project root, not the CWD
_PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(_PACKAGE_ROOT, "data")
USERS_PATH = os.path.join(DATA_DIR, "usuarios.json")

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

        # Cargar usuarios usando from_dict; tolerar entradas legacy
        users = []
        for u in data:
            try:
                users.append(User.from_dict(u))
            except Exception:
                # Ignorar registros que no encajan con el modelo actual
                continue
        return users

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([u.to_dict() for u in self.users], f, ensure_ascii=False, indent=4)

    def add_user(self, user: User):
        self.users.append(user)

    def find_by_email(self, email: str):
        for u in self.users:
            if u.email.lower() == email.lower():
                return u
        return None
    
    def get_all(self):
        return self.users
