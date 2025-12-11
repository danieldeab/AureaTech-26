from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional
from uuid import UUID, uuid4
from .enums import RoleEnum

@dataclass(slots=True)
class User:
    id: UUID
    community_id: int
    name: str
    email: str
    password_hash: str
    role: RoleEnum
    picture_path: Optional[str] = None
    picture_url: Optional[str] = None

    @staticmethod
    def new(name: str, email: str, password_hash: str, role: RoleEnum, community_id: int) -> "User":
        return User(id=uuid4(), name=name, email=email, password_hash=password_hash, role=role, community_id=community_id)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["id"] = str(self.id)
        d["role"] = self.role.value
        return d

    @staticmethod
    def from_dict(d: dict) -> "User":
        return User(
            id=UUID(d["id"]),
            community_id=d["community_id"],
            name=d["name"],
            email=d["email"],
            password_hash=d["password_hash"],
            role=RoleEnum(d["role"]),
            picture_path=d.get("picture_path"),
            picture_url=d.get("picture_url"),
        )
