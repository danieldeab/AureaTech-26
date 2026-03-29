import json
import os
from app.model.user import User
from app.repository.interfaces.user_repository_interface import IUserRepository

# Always resolve data path relative to the project root, not the CWD
_PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(_PACKAGE_ROOT, "data")
USERS_PATH = os.path.join(DATA_DIR, "usuarios.json")

from app.model.reading import Reading
from app.repository.interfaces.reading_repository_interface import IReadingRepository

class UserRepository(IUserRepository):
    def __init__(self, path=USERS_PATH):
        self.path = path
        self.users = self._load()

    """""
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
    """""


def save(self):
    # tmp_path = self.path + ".tmp"
    # with open(tmp_path, "w", encoding="utf-8") as f:
    #     json.dump([u.to_dict() for u in self.users], f, ensure_ascii=False, indent=4)
    # os.replace(tmp_path, self.path)
    pass

def add_user(self, user: User):


    """
    En la tabla users el orden sería:
    [
        community_id,
        full_name,
        email,
        password_hash,
        role,
        date_of_birth,
        picture_path,
        picture_url
    ]
    user_id, created_at y updated_at se generan solos en la BD
    """

    data = [
        user.community_id,
        user.full_name,
        user.email,
        user.password_hash,
        user.role.value if hasattr(user.role, 'value') else user.role,
        user.date_of_birth,
        user.picture_path,
        user.picture_url
    ]

    self.db.add("users", data)

def find_by_email(self, email: str):
    # email = email.strip().lower()
    # for u in self.users:
    #     if u.email.lower() == email:
    #         return u
    # return None

    response = self.db.select("users", "email", email.strip().lower())

    if not response:
        return None

    row = response[0]
    return User(
        row[0],   # user_id
        row[1],   # community_id
        row[2],   # full_name
        row[3],   # email
        row[4],   # password_hash
        row[5],   # role
        row[6],   # date_of_birth
        row[7],   # picture_path
        row[8],   # picture_url
        row[9],   # created_at
        row[10]   # updated_at
    )

def update_role(self, user_id: str, new_role: str):
    # for u in self.users:
    #     if str(u.id) == str(user_id):
    #         from app.model.enums import RoleEnum
    #         u.role = RoleEnum(new_role)
    #         self.save()
    #         return u
    # return None

    self.db.update("users", "user_id", user_id, "role", new_role)
    return self.find_by_id(user_id)

def update_community(self, user_id: str, new_community_id: int):
    # for u in self.users:
    #     if str(u.id) == str(user_id):
    #         u.community_id = new_community_id
    #         self.save()
    #         return u
    # return None

    self.db.update("users", "user_id", user_id, "community_id", new_community_id)
    return self.find_by_id(user_id)

def find_by_community_id(self, community_id: int):
    # users = []
    # for u in self.users:
    #     if u.community_id == community_id:
    #         users.append(u)
    # return users

    response = self.db.select("users", "community_id", community_id)

    users = []
    for row in response:
        user = User(
            row[0],   # user_id
            row[1],   # community_id
            row[2],   # full_name
            row[3],   # email
            row[4],   # password_hash
            row[5],   # role
            row[6],   # date_of_birth
            row[7],   # picture_path
            row[8],   # picture_url
            row[9],   # created_at
            row[10]   # updated_at
        )
        users.append(user)

    return users

def find_by_community_id_and_role(self, community_id: str, role: str):
    # users = []
    # for u in self.users:
    #     if u.community_id == community_id and u.role.value == role:
    #         users.append(u)
    # return users

    response = self.db.select_by_two_fields("users", "community_id", community_id, "role", role)

    users = []
    for row in response:
        user = User(
            row[0],   # user_id
            row[1],   # community_id
            row[2],   # full_name
            row[3],   # email
            row[4],   # password_hash
            row[5],   # role
            row[6],   # date_of_birth
            row[7],   # picture_path
            row[8],   # picture_url
            row[9],   # created_at
            row[10]   # updated_at
        )
        users.append(user)

    return users

def get_all(self):
    # return self.users

    response = self.db.select_all("users")

    users = []
    for row in response:
        user = User(
            row[0],   # user_id
            row[1],   # community_id
            row[2],   # full_name
            row[3],   # email
            row[4],   # password_hash
            row[5],   # role
            row[6],   # date_of_birth
            row[7],   # picture_path
            row[8],   # picture_url
            row[9],   # created_at
            row[10]   # updated_at
        )
        users.append(user)

    return users

def get_all_communities(self):
    # comm_ids = set()
    # for u in self.users:
    #     if u.community_id is not None:
    #         comm_ids.add(u.community_id)
    # return sorted(comm_ids)

    response = self.db.select_all("users")

    comm_ids = set()
    for row in response:
        community_id = row[1]  # community_id
        if community_id is not None:
            comm_ids.add(community_id)

    return sorted(comm_ids)

def delete_user(self, user_id: str):
    # self.users = [u for u in self.users if str(u.id) != str(user_id)]
    # self.save()

    self.db.delete("users", "user_id", user_id)

def find_by_id(self, user_id: str):
    response = self.db.select("users", "user_id", user_id)

    if not response:
        return None

    row = response[0]
    return User(
        row[0],   # user_id
        row[1],   # community_id
        row[2],   # full_name
        row[3],   # email
        row[4],   # password_hash
        row[5],   # role
        row[6],   # date_of_birth
        row[7],   # picture_path
        row[8],   # picture_url
        row[9],   # created_at
        row[10]   # updated_at
    )