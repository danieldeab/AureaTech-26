from app.model.user import User
from app.utils.session import Session
from app.repository.interfaces.user_repository_interface import IUserRepository
from app.repository.interfaces.log_repository_interface import ILogRepository
from app.model.log_entry import LogEntry
from app.model.enums import RoleEnum

import hashlib
import os
import shutil
import re
from datetime import datetime


class AuthController:
    """
    Final authentication controller aligned with the new domain User model.
    """

    def __init__(self, repo: IUserRepository, session: Session, logs: ILogRepository):
        self.repo = repo
        self.session = session
        self.log_repo = logs

    def _hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _valid_email(self, correo):
        return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", correo) is not None

    def _normalize_dob(self, dob: str | None) -> str | None:
        """
        Normalize incoming DOB to YYYY-MM-DD for MariaDB DATE columns.
        Accepts:
        - YYYY-MM-DD
        - DD/MM/YYYY
        - DD-MM-YYYY
        """
        if not dob:
            return None

        dob = dob.strip()

        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(dob, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue

        raise ValueError("Formato de fecha inválido. Use DD/MM/YYYY o YYYY-MM-DD.")

    def _log(self, action, details: str, *, actor_id: int = 1, actor_role: RoleEnum = RoleEnum.ADMIN):
        if self.session.current_user:
            actor_id = int(self.session.current_user.id)
            actor_role = self.session.current_user.role

        log = LogEntry.new(
            actor_id=int(actor_id),
            actor_role=actor_role,
            category="AUTH",
            action=action,
            details=details,
        )
        self.log_repo.add(log)

    def login(self, correo, password):
        if not correo or not password:
            return False, "Please enter both email and password.", None

        if not self._valid_email(correo):
            return False, "Invalid email format.", None

        hashed = self._hash(password)
        finder = getattr(self.repo, "find_by_email_and_password_hash", None)
        user = finder(correo, hashed) if callable(finder) else None

        if user is None:
            user = self.repo.find_by_email(correo)
            if not user or user.password_hash != hashed:
                return False, "Wrong credentials. Please try again.", None

        self.session.set_current_user(user)
        self.session.current_community_id = user.community_id
        self._log(action="login_ok", details=correo, actor_id=int(user.id), actor_role=user.role)

        return True, "Login successful.", user

    def signup(self, name: str, community_id: str, email: str, password: str, dob: str, picture_temp_path: str | None):
        if not (name and email and password and dob):
            return "Nombre, email y contraseña son campos obligatorios."

        if not self._valid_email(email):
            return "Formato de correo inválido."

        if self.repo.find_by_email(email):
            return "El correo ya está registrado."

        try:
            normalized_dob = self._normalize_dob(dob)
        except ValueError as e:
            return str(e)

        hashed = self._hash(password)
        final_picture_path = None

        if picture_temp_path:
            ext = os.path.splitext(picture_temp_path)[1].lower()
            if ext not in [".jpg", ".jpeg", ".png"]:
                return "Formato de imagen no soportado."

            dest_dir = "data/profile_pictures"
            os.makedirs(dest_dir, exist_ok=True)

            filename = f"{hashed[:12]}{ext}"
            final_picture_path = os.path.join(dest_dir, filename)
            shutil.copy2(picture_temp_path, final_picture_path)

        new_user = User.new(
            name=name,
            email=email.lower(),
            password_hash=hashed,
            role=RoleEnum.NEIGHBOR,
            community_id=int(community_id),
            dob=normalized_dob,
        )
        new_user.picture_path = final_picture_path
        new_user.picture_url = None

        created = self.repo.add_user(new_user)
        self._log(action="signup_ok", details=email, actor_id=int(created.id), actor_role=created.role)
        return True

    def recover_password(self, email: str):
        if not email:
            return False, "Introduce un correo."

        if not self._valid_email(email):
            return False, "Formato de correo inválido."

        user = self.repo.find_by_email(email)
        actor_id = int(user.id) if user and user.id is not None else 1
        actor_role = user.role if user else RoleEnum.ADMIN

        self._log(action="recover_request", details=email, actor_id=actor_id, actor_role=actor_role)

        if not user:
            return False, "Si el correo existe, se enviará un enlace de recuperación."

        self.session.start_reset(user.email)
        return True, "Si el correo existe, se enviará un enlace de recuperación."

    def update_password(self, pass1: str, pass2: str):
        if not (pass1 and pass2):
            return "Rellena ambos campos."

        if pass1 != pass2:
            return "Las contraseñas no coinciden."

        email = self.session.reset_email
        if not email:
            self._log(action="reset_attempt_no_session", details="unknown")
            return "Sesión expirada."

        user = self.repo.find_by_email(email)
        if not user:
            return "Usuario no encontrado."

        user.password_hash = self._hash(pass1)

        save_fn = getattr(self.repo, "save", None)
        if callable(save_fn):
            save_fn(user)

        self._log(action="reset_success", details=user.email, actor_id=int(user.id), actor_role=user.role)
        self.session.clear_reset()
        return "Contraseña actualizada con éxito."

    def logout(self):
        self.session.clear()