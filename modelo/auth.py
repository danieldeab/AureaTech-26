# modelo/auth.py
import hashlib
from typing import Optional, List, Tuple
from modelo.Models import User, Session  # 👈 import correcto

def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

class UserRepository:
    """
    Repositorio en memoria con un usuario de prueba:
    email: test@demo.com
    pass : 123456
    """
    def __init__(self):
        self._users: List[User] = [
            User(
                id=1,
                email="test@demo.com",
                password_hash=_sha256("123456"),
                display_name="Usuario Demo",
            ),
        ]

    def find_by_email(self, email: str) -> Optional[User]:
        email = (email or "").strip().lower()
        for u in self._users:
            if u.email.lower() == email:
                return u
        return None

    def verify_password(self, user: User, raw_password: str) -> bool:
        return user.password_hash == _sha256((raw_password or "").strip())

class AuthController:
    def __init__(self, repo: UserRepository, session: Session):
        self.repo = repo
        self.session = session

    def login(self, email: str, password: str) -> Tuple[bool, str]:
        email = (email or "").strip()
        password = (password or "").strip()

        if not email or not password:
            return False, "Advertencia: Hay campos vacíos."

        user = self.repo.find_by_email(email)
        if not user:
            return False, "Error: Usuario no encontrado."

        if not self.repo.verify_password(user, password):
            return False, "Error: Credenciales incorrectas."

        self.session.current_user = user
        return True, f"Inicio correcto. Bienvenido, {user.display_name}."

    def logout(self) -> None:
        self.session.current_user = None
