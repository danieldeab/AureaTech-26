from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional
from .enums import RoleEnum


@dataclass(slots=True)
class User:
    id: int | None
    community_id: int
    name: str
    email: str
    password_hash: str
    role: RoleEnum
    dob: Optional[str] = None
    picture_path: Optional[str] = None
    picture_url: Optional[str] = None
    is_active: bool = True

    @staticmethod
    def new(
        name: str,
        email: str,
        password_hash: str,
        role: RoleEnum,
        community_id: int,
        dob: str | None = None,
        is_active: bool = True,
    ) -> "User":
        return User(
            id=None,
            community_id=community_id,
            name=name,
            email=email,
            password_hash=password_hash,
            role=role,
            dob=dob,
            picture_path=None,
            picture_url=None,
            is_active=is_active,
        )

    def to_dict(self) -> dict:
        d = asdict(self)
        d["id"] = str(self.id) if self.id is not None else None
        d["role"] = self.role.value
        return d

    @staticmethod
    def from_dict(d: dict) -> "User":
        return User(
            id=d.get("id"),
            community_id=d["community_id"],
            name=d["name"],
            email=d["email"],
            password_hash=d["password_hash"],
            role=RoleEnum(d["role"]),
            dob=d.get("dob"),
            picture_path=d.get("picture_path"),
            picture_url=d.get("picture_url"),
            is_active=bool(d.get("is_active", True)),
        )