from __future__ import annotations
from typing import List, Optional
from uuid import UUID

from app.model.user import User
from app.model.enums import RoleEnum
from app.repository.interfaces.user_repository_interface import IUserRepository
from app.service.audit_log_service import AuditLogService
from app.service.error_service import ErrorService
from app.service.password_service import hash_password


class UserService:
    """DB-backed user management service."""

    def __init__(
        self,
        user_repo: IUserRepository,
        audit_log_service: AuditLogService | None = None,
        error_service: ErrorService | None = None,
    ):
        self.repo = user_repo
        self.audit_log_service = audit_log_service or AuditLogService()
        self.error_service = error_service or ErrorService()

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
        try:
            new_user = User.new(
                name=fullname,
                email=email.lower(),
                password_hash=hash_password(password),
                dob=dob,
                role=role,
                community_id=int(community_id),
            )
            new_user.picture_path = picture_path
            created = self.repo.add_user(new_user)
            self.audit_log_service.log(
                actor_id=1,
                actor_role=RoleEnum.ADMIN,
                category="USER",
                action="user_create",
                details=f"Created user {created.email}",
                community_id=created.community_id,
                target_entity_type="user",
                target_entity_id=int(created.id),
            )
            return created
        except Exception as exc:
            self.error_service.capture_exception(exc, source_layer="SERVICE")
            raise

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
        original_community_id = target_user.community_id
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
            persisted_user = persisted or target_user
            self.audit_log_service.log(
                actor_id=1,
                actor_role=RoleEnum.ADMIN,
                category="USER",
                action="user_update",
                details=f"Updated user {persisted_user.email}",
                community_id=persisted_user.community_id or original_community_id,
                target_entity_type="user",
                target_entity_id=int(persisted_user.id),
            )
            return persisted or target_user
        return target_user

    def admin_delete_user(self, user: User) -> None:
        delete_fn = getattr(self.repo, "delete_user", None)
        if callable(delete_fn) and user.id is not None:
            delete_fn(str(user.id))
            self.audit_log_service.log(
                actor_id=1,
                actor_role=RoleEnum.ADMIN,
                category="USER",
                action="user_delete",
                details=f"Deleted user {user.email}",
                community_id=user.community_id,
                target_entity_type="user",
                target_entity_id=int(user.id),
            )

    def update_own_profile(
        self,
        user: User,
        *,
        fullname: Optional[str] = None,
        email: Optional[str] = None,
        dob: Optional[str] = None,
        picture_path: Optional[str] = None,
    ) -> User:
        try:
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
                persisted_user = persisted or user
                self.audit_log_service.log(
                    actor_id=int(persisted_user.id),
                    actor_role=persisted_user.role,
                    category="USER",
                    action="user_update",
                    details=f"Updated own profile ({persisted_user.email})",
                    community_id=persisted_user.community_id,
                    target_entity_type="user",
                    target_entity_id=int(persisted_user.id),
                )
                return persisted_user
            return user
        except Exception as exc:
            self.error_service.capture_exception(
                exc,
                source_layer="SERVICE",
                user_id=int(user.id) if user.id is not None else None,
                community_id=user.community_id,
                target_entity_type="user",
                target_entity_id=int(user.id) if user.id is not None else None,
            )
            raise
