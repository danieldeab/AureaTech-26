# modelo/auth.py
import hashlib
import json
import os
from dataclasses import asdict
from typing import Optional, List, Tuple
from model.Models import User, Session

USERS_FILE = os.path.join(os.path.dirname(__file__), "usuarios.json")

def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

class UserRepository:
    def __init__(self):
        if not os.path.exists(USERS_FILE):
            demo_user = {
                "id": 1,
                "email": "test@demo.com",
                "password": "123456",
                "password_hash": _sha256("123456"),
                "display_name": "Usuario Demo",
            }
            with open(USERS_FILE, "w", encoding="utf-8") as f:
                json.dump([demo_user], f, indent=4, ensure_ascii=False)
        self._users: List[User] = self._load_users()

    def _load_users(self) -> List[User]:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for u in data:
            if "password_hash" not in u:
                u["password_hash"] = _sha256(u.get("password", "") or "")
            if "password" not in u:
                u["password"] = None
        users: List[User] = []
        for u in data:
            users.append(User(
                id=u["id"],
                email=u["email"],
                password_hash=u["password_hash"],
                display_name=u["display_name"],
                password=u.get("password"),
            ))
        return users

    def _save_users(self):
        data = [asdict(u) for u in self._users]
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # ---------- públicos ----------
    def find_by_email(self, email: str) -> Optional[User]:
        email = (email or "").strip().lower()
        for u in self._users:
            if u.email.lower() == email:
                return u
        return None

    def verify_password(self, user: User, raw_password: str) -> bool:
        return user.password_hash == _sha256((raw_password or "").strip())

    def add_user(self, email: str, password: str, display_name: str) -> Tuple[bool, str]:
        email_n = (email or "").strip().lower()
        if self.find_by_email(email_n):
            return False, "Error: El usuario ya existe."
        new_user = User(
            id=(max([u.id for u in self._users]) + 1) if self._users else 1,
            email=email_n,
            password_hash=_sha256(password),
            display_name=(display_name or "").strip(),
            password=password,  # se guarda en texto plano (solo DEV)
        )
        self._users.append(new_user)
        self._save_users()
        return True, f"Usuario {new_user.display_name} registrado con éxito."

    # ✅ NUEVO: actualizar contraseña
    def update_password(self, email: str, new_password: str) -> Tuple[bool, str]:
        user = self.find_by_email(email)
        if not user:
            return False, "No existe una cuenta con ese correo."
        user.password_hash = _sha256(new_password)
        user.password = new_password     # visible en JSON (solo DEV)
        self._save_users()
        return True, "Contraseña actualizada."

class AuthController:
    def __init__(self, repo: UserRepository, session: Session):
        self.repo = repo
        self.session = session

    def login(self, email: str, password: str) -> Tuple[bool, str]:
        if not email or not password:
            return False, "Advertencia: Hay campos vacíos."
        user = self.repo.find_by_email(email)
        if not user:
            return False, "Error: Usuario no encontrado."
        if not self.repo.verify_password(user, password):
            return False, "Error: Credenciales incorrectas."
        self.session.current_user = user
        return True, f"Inicio correcto. Bienvenido, {user.display_name}."

    def logout(self):
        self.session.clear()
