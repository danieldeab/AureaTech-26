from __future__ import annotations

from typing import Optional

from app.model.user import User
from app.infraestructure.db import get_db
from app.model.enums import RoleEnum
from app.repository.interfaces.user_repository_interface import IUserRepository


class UserRepository(IUserRepository):
    def __init__(self):
        self.db = get_db()

    def _row_to_user(self, row: dict) -> User:
        return User(
            id=row["user_id"],
            community_id=row["community_id"],
            name=row["full_name"],
            email=row["email"],
            password_hash=row["password_hash"],
            role=RoleEnum(row["role"]),
            dob=row["date_of_birth"],
            picture_path=row["picture_path"],
            picture_url=row["picture_url"],
            is_active=bool(row.get("is_active", 1)),
        )

    def _user_to_db_data(self, user: User) -> dict:
        return {
            "community_id": user.community_id,
            "full_name": user.name,
            "email": user.email.strip().lower(),
            "password_hash": user.password_hash,
            "role": user.role.value if isinstance(user.role, RoleEnum) else str(user.role),
            "date_of_birth": user.dob,
            "picture_path": user.picture_path,
            "picture_url": user.picture_url,
            "is_active": int(bool(getattr(user, "is_active", True))),
        }

    def find_by_email(self, email: str):
        norm_email = email.strip().lower()
        row = self.db.fetch_one(
            table="user",
            where={
                "email": norm_email,
                "is_active": 1,
            },
        )
        return self._row_to_user(row) if row else None

    def find_by_email_and_password_hash(self, email: str, password_hash: str):
        row = self.db.fetch_one(
            table="user",
            where={
                "email": email.strip().lower(),
                "password_hash": password_hash,
                "is_active": 1,
            },
        )
        return self._row_to_user(row) if row else None

    def find_by_community_id(self, community_id: int):
        rows = self.db.fetch_all(
            table="user",
            where={
                "community_id": int(community_id),
                "is_active": 1,
            },
            order_by="user_id ASC",
        )
        return [self._row_to_user(row) for row in rows]

    def add_user(self, user: User):
        new_id = self.db.insert(
            table="user",
            data=self._user_to_db_data(user),
        )
        user.id = new_id
        return user

    def save(self, user: Optional[User] = None):
        if user is None:
            return None

        if user.id is None:
            return self.add_user(user)

        self.db.update(
            table="user",
            data=self._user_to_db_data(user),
            where={"user_id": int(user.id)},
        )
        return self.find_by_id(str(user.id))

    def get_all(self):
        rows = self.db.fetch_all(
            table="user",
            where={"is_active": 1},
            order_by="user_id ASC",
        )
        return [self._row_to_user(row) for row in rows]

    def update_role(self, user_id: str, new_role: str):
        role_value = new_role.value if isinstance(new_role, RoleEnum) else str(new_role)
        self.db.update(
            table="user",
            data={"role": role_value},
            where={"user_id": int(user_id)},
        )
        return self.find_by_id(user_id)

    def update_community(self, user_id: str, new_community_id: int):
        self.db.update(
            table="user",
            data={"community_id": int(new_community_id)},
            where={"user_id": int(user_id)},
        )
        return self.find_by_id(user_id)

    def find_by_community_id_and_role(self, community_id: str, role: str):
        role_value = role.value if isinstance(role, RoleEnum) else str(role).upper()
        rows = self.db.fetch_all(
            table="user",
            where={
                "community_id": int(community_id),
                "role": role_value,
                "is_active": 1,
            },
            order_by="user_id ASC",
        )
        return [self._row_to_user(row) for row in rows]

    def get_all_communities(self):
        rows = self.db.fetch_all(
            table="community",
            columns=["community_id", "name", "address"],
            order_by="community_id ASC",
        )
        return sorted({row["community_id"] for row in rows if row["community_id"] is not None})

    def delete_user(self, user_id: str):
        """
        Logical delete / baja.
        """
        return self.db.update(
            table="user",
            data={"is_active": 0},
            where={"user_id": int(user_id)},
        )

    def find_by_id(self, user_id: str):
        row = self.db.fetch_one(
            table="user",
            where={"user_id": int(user_id)},
        )
        return self._row_to_user(row) if row else None