# app/service/user_service.py

from __future__ import annotations
from typing import List, Optional
from uuid import UUID

from app.model.user import User
from app.model.enums import RoleEnum
from app.repository.interfaces.user_repository_interface import IUserRepository


class UserService:
    """
    Service for user management.
    Implements role-based permissions and community filtering.

    Rules under Option B:
    - Admin can:
        * View users ONLY in the selected community
        * Create new neighbors/technicians
        * Update or delete users in that community
    - Neighbors/Technicians:
        * Can view + update only their own data
    """

    def __init__(self, user_repo: IUserRepository):
        self.repo = user_repo

    # ----------------------------------------------------------------------
    # FETCHING USERS
    # ----------------------------------------------------------------------

    def get_users_in_community(self, community_id: int) -> List[User]:
        """Return all users belonging to a given community."""
        users = self.repo.get_all()
        return [u for u in users if u.community_id == community_id]

    def get_user(self, user_id: str | UUID) -> Optional[User]:
        """Return a single user by ID."""
        uid = str(user_id)
        for u in self.repo.get_all():
            if str(u.id) == uid:
                return u
        return None

    # ----------------------------------------------------------------------
    # ADMIN ACTIONS
    # ----------------------------------------------------------------------

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
        """
        Admin creates a neighbor or technician.
        (Admins themselves cannot be created by admins in PI1 context.)
        """
        new_user = User.new(
            fullname=fullname,
            email=email,
            password=password,
            dob=dob,
            role=role,
            community_id=community_id,
            picture_path=picture_path,
        )
        self.repo.add_user(new_user)
        self.repo.save()
        return new_user

    def admin_update_user(
        self,
        target_user: User,
        *,
        fullname: Optional[str] = None,
        email: Optional[str] = None,
        dob: Optional[str] = None,
        role: Optional[RoleEnum] = None,
        community_id: Optional[int] = None,
        picture_path: Optional[str] = None
    ) -> User:
        """
        Admin modifies a user in the selected community.
        Only attributes provided are updated.
        """

        if fullname is not None:
            target_user.fullname = fullname
        if email is not None:
            target_user.email = email.lower()
        if dob is not None:
            target_user.dob = dob
        if role is not None:
            target_user.role = role
        if community_id is not None:
            target_user.community_id = community_id
        if picture_path is not None:
            target_user.picture_path = picture_path

        self.repo.save()
        return target_user

    def admin_delete_user(self, user: User) -> None:
        """Admin deletes a user from the repository."""
        all_users = self.repo.get_all()
        remaining = [u for u in all_users if u.id != user.id]

        # rewrite file by overriding repo's internal list:
        self.repo.users = remaining                # type: ignore[attr-defined]
        self.repo.save()

    # ----------------------------------------------------------------------
    # USER SELF-UPDATE (NEIGHBOR)
    # ----------------------------------------------------------------------

    def update_own_profile(
        self,
        user: User,
        *,
        fullname: Optional[str] = None,
        email: Optional[str] = None,
        dob: Optional[str] = None,
        picture_path: Optional[str] = None,
    ) -> User:
        """
        Neighbors or technicians may update only their own profile details.
        Cannot change community or role.
        """

        if fullname is not None:
            user.fullname = fullname
        if email is not None:
            user.email = email.lower()
        if dob is not None:
            user.dob = dob
        if picture_path is not None:
            user.picture_path = picture_path

        self.repo.save()
        return user
