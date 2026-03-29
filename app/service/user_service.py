from __future__ import annotations
from typing import List, Optional
from uuid import UUID
import hashlib

from app.model.user import User
from app.model.enums import RoleEnum
from app.repository.interfaces.user_repository_interface import IUserRepository


class UserService:
    """DB-backed user management service."""

    def __init__(self, user_repo: IUserRepository):
        self.repo = user_repo

    def get_users_in_community(self, community_id: int) -> List[User]:
        finder = getattr(self.repo, "find_by_community_id", None)
        if callable(finder):
            return finder(int(community_id))
        users = self.repo.get_all()
        return [u for u in users if u.community_id == community_id]

    def get_user(self, user_id: str | UUID) -> Optional[User]:
        finder = getattr(self.repo, "find_by_id", None)
        if callable(finder):
            return finder(str(user_id))
        uid = str(user_id)
        for u in self.repo.get_all():
            if str(u.id) == uid:
                return u
        return None

    def admin_create_user(
        self,
        fullname: str,
        email: str,
        password: str,
        dob: str,
        role: RoleEnum,
        community_id: int,
        picture_path: Optional[str] = None,
    ) -> User:
        new_user = User.new(
            name=fullname,
            email=email.lower(),
            password_hash=hashlib.sha256(password.encode("utf-8")).hexdigest(),
            dob=dob,
            role=role,
            community_id=int(community_id),
        )
        new_user.picture_path = picture_path
        return self.repo.add_user(new_user)

    def admin_update_user(
        self,
        target_user: User,
        *,
        fullname: Optional[str] = None,
        email: Optional[str] = None,
        dob: Optional[str] = None,
        role: Optional[RoleEnum] = None,
        community_id: Optional[int] = None,
        picture_path: Optional[str] = None,
    ) -> User:
        if fullname is not None:
            target_user.name = fullname
        if email is not None:
            target_user.email = email.lower()
        if dob is not None:
            target_user.dob = dob
        if role is not None:
            target_user.role = role
        if community_id is not None:
            target_user.community_id = int(community_id)
        if picture_path is not None:
            target_user.picture_path = picture_path

        save_fn = getattr(self.repo, "save", None)
        if callable(save_fn):
            persisted = save_fn(target_user)
            return persisted or target_user
        return target_user

    def admin_delete_user(self, user: User) -> None:
        delete_fn = getattr(self.repo, "delete_user", None)
        if callable(delete_fn) and user.id is not None:
            delete_fn(str(user.id))

    def update_own_profile(
        self,
        user: User,
        *,
        fullname: Optional[str] = None,
        email: Optional[str] = None,
        dob: Optional[str] = None,
        picture_path: Optional[str] = None,
    ) -> User:
        if fullname is not None:
            user.name = fullname
        if email is not None:
            user.email = email.lower()
        if dob is not None:
            user.dob = dob
        if picture_path is not None:
            user.picture_path = picture_path

        save_fn = getattr(self.repo, "save", None)
        if callable(save_fn):
            persisted = save_fn(user)
            return persisted or user
        return user