# app/controller/auth_controller.py

from app.model.models import User, Session
from app.repository.user_repository import UserRepository
from app.repository.log_repository import LogRepository
from app.repository.interfaces.user_repository_interface import IUserRepository
from app.repository.interfaces.log_repository_interface import ILogRepository
import hashlib, os, shutil, re
from uuid import uuid4


class AuthController:
    """
    Final authentication controller.
    Contains all logic requested by UIController:
        - login
        - signup
        - recover_password
        - update_password
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
        # simple RFC-5322–safe pattern used for UI validation
        return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", correo) is not None    

    def _log(self, action, email, role):
        self.log_repo.add({
            "action": action,
            "email": email,
            "role": role,
        })

    # ==========================================
    # LOGIN
    # ==========================================
    def login(self, correo, password):
        # 1) required fields
        if not correo or not password:
            return False, "Please enter both email and password.", None

        # 2) email format
        if not self._valid_email(correo):
            return False, "Invalid email format.", None

        # 3) authenticate using repository only
        user = self.repo.find_by_email(correo)
        if not user:
            return False, "Wrong credentials. Please try again.", None

        hashed = self._hash(password)
        if user.password != hashed:
            return False, "Wrong credentials. Please try again.", None

        # 4) success → set session
        self.session.set_current_user(user)

        # 5) log the event
        self._log("login_ok", correo, getattr(user, "role", "unknown"))

        return True, "Login successful.", user

    # ==========================================
    # SIGNUP
    # ==========================================
    def signup(self, name: str, email: str, password: str, dob: str, picture_temp_path: None):
        if not (name and email and password and dob):
            return "Nombre, email y contraseña son campos obligatorios."

        if not self._valid_email(email):
            return "Formato de correo inválido."

        if self.repo.find_by_email(email):
            return "El correo ya está registrado."

        hashed = self._hash(password)
        final_picture_path = None

        if picture_temp_path:
            # Save profile picture to permanent location
            ext = os.path.splitext(picture_temp_path)[1].lower()
            if ext not in [".jpg", ".jpeg", ".png"]:
                return "Formato de imagen no soportado."
            else:
                dest_dir = "data/profile_pictures"
                os.makedirs(dest_dir, exist_ok=True)

                filename = f"{uuid4().hex}{ext}"
                final_picture_path = os.path.join(dest_dir, filename)
                shutil.copy2(picture_temp_path, final_picture_path)

        user = User(
            fullname=name,
            email=email.lower(),
            password=hashed,
            dob=dob,
            role="vecino",    # default role
            picture_path=final_picture_path  # optional
        )

        self.repo.add_user(user)
        self.repo.save()
        
        self._log("signup_ok", email, "vecino")
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

        # Log request even if user does not exist
        self._log("recover_request", email, user.role if user else "unknown")

        # Temp reset session for MVP coherence
        if user:
            self.session.set_current_user(user)
        return "Si el correo existe, se enviará un enlace de recuperación."

    # ==========================================
    # UPDATE PASSWORD
    # ==========================================
    def update_password(self, pass1: str, pass2: str):
        if not (pass1 and pass2):
            return "Rellena ambos campos."

        if pass1 != pass2:
            return "Las contraseñas no coinciden."

        user = self.session.get_current_user()
        if not user:
            # Log the failed attempt
            self._log("reset_attempt_no_session", "unknown", "unknown")
            return "Sesión expirada."
        else:
            user.password = self._hash(pass1)
            self.repo.save()

            self._log("reset_success", user.email, user.role)
            return "Contraseña actualizada con éxito."

    # ==========================================
    # LOGOUT
    # ==========================================
    def logout(self):
        self.session.clear()
