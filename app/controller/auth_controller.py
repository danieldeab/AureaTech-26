# app/controller/auth_controller.py

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
from uuid import uuid4


class AuthController:
    """
    Final authentication controller aligned with the new domain User model.
    """

    def __init__(self, repo: IUserRepository, session: Session, logs: ILogRepository):
        self.repo = repo
        self.session = session
        self.log_repo = logs

    # ==========================================
    # Utilities
    # ==========================================
    def _hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _valid_email(self, correo):
        return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", correo) is not None

    def _log(self, action, details: str):
        if self.session.current_user:
            actor_id = self.session.current_user.id
            actor_role = self.session.current_user.role
        else:
            actor_id = uuid4()
            actor_role = RoleEnum.NEIGHBOR

        log = LogEntry.new(
            actor_id=actor_id,
            actor_role=actor_role,
            category="AUTH",
            action=action,
            details=details,
        )

        self.log_repo.add(log)

    # ==========================================
    # LOGIN
    # ==========================================
    def login(self, correo, password):
        if not correo or not password:
            return False, "Please enter both email and password.", None

        if not self._valid_email(correo):
            return False, "Invalid email format.", None

        user = self.repo.find_by_email(correo)
        if not user:
            return False, "Wrong credentials. Please try again.", None

        hashed = self._hash(password)
        if user.password_hash != hashed:
            return False, "Wrong credentials. Please try again.", None

        # success
        self.session.set_current_user(user)
        self.session.current_community_id = user.community_id

        self._log(action="login_ok", details=correo)

        return True, "Login successful.", user

    # ==========================================
    # SIGNUP
    # ==========================================
    def signup(self, name: str, community_id: str, email: str, password: str, dob: str, picture_temp_path: str | None):
        if not (name and email and password and dob):
            return "Nombre, email y contraseña son campos obligatorios."

        if not self._valid_email(email):
            return "Formato de correo inválido."

        if self.repo.find_by_email(email):
            return "El correo ya está registrado."

        hashed = self._hash(password)

        # --------------------------------------
        # Handle profile picture (optional)
        # --------------------------------------
        final_picture_path = None

        if picture_temp_path:
            ext = os.path.splitext(picture_temp_path)[1].lower()
            if ext not in [".jpg", ".jpeg", ".png"]:
                return "Formato de imagen no soportado."

            dest_dir = "data/profile_pictures"
            os.makedirs(dest_dir, exist_ok=True)

            filename = f"{uuid4().hex}{ext}"
            final_picture_path = os.path.join(dest_dir, filename)
            shutil.copy2(picture_temp_path, final_picture_path)

        # --------------------------------------
        # Create proper domain User
        # --------------------------------------
        new_user = User.new(
            name=name,
            community_id=int(community_id),
            email=email.lower(),
            password_hash=hashed,
            role=RoleEnum.NEIGHBOR,
            dob=dob,
        )

        # Attach optional fields
        new_user.picture_path = final_picture_path
        new_user.picture_url = None

        self.repo.add_user(new_user)
        self.repo.save()

        self._log(action="signup_ok", details=email)
        return True

    # ==========================================
    # RECOVER PASSWORD
    # ==========================================
    def recover_password(self, email: str):
        if not email:
            return "Introduce un correo."

        if not self._valid_email(email):
            return "Formato de correo inválido."

        user = self.repo.find_by_email(email)

        self._log(
            action="recover_request",
            details=email
        )

        if not user:
            return False, "Si el correo existe, se enviará un enlace de recuperación."
        else:
            self.session.start_reset(user.email)
            return True, "Si el correo existe, se enviará un enlace de recuperación."

    # ==========================================
    # UPDATE PASSWORD
    # ==========================================
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
        
        # update password
        user.password_hash = self._hash(pass1)
        self.repo.save()

        self._log(action="reset_success", details=user.email)

        # End reset session
        self.session.clear_reset()
        return "Contraseña actualizada con éxito."

    # ==========================================
    # LOGOUT
    # ==========================================
    def logout(self):
        self.session.clear()
