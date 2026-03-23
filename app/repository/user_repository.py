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

        # Load using the domain factory
        loaded = []
        for u in data:
            try:
                loaded.append(User.from_dict(u))
            except Exception as e:
                print(f"[UserRepository] Error loading user: {e}\nUser data: {u}")
        return loaded
    
    def save(self):
        # Using temp to avoid unfinished transactions from corruopting data
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
    
    def update_role(self, user_id: str, new_role: str):
        for u in self.users:
            if str(u.id) == str(user_id):
                from app.model.enums import RoleEnum
                u.role = RoleEnum(new_role)     # convert string → enum
                self.save()
                return u
        return None
    
    def update_community(self, user_id: str, new_community_id: int):
        for u in self.users:
            if str(u.id) == str(user_id):
                u.community_id = new_community_id
                self.save()
                return u
        return None

    def find_by_community_id(self, community_id: int):
        users = []
        for u in self.users:
            if u.community_id == community_id:
                users.append(u)
        return users

    def get_all(self):
        return self.users
    
    def get_all_communities(self):
        comm_ids = set()
        for u in self.users:
            if u.community_id is not None:
                comm_ids.add(u.community_id)
        return sorted(comm_ids)
    
    def delete_user(self, user_id: str):
        self.users = [u for u in self.users if str(u.id) != str(user_id)]
        self.save()