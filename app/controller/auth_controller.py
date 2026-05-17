from app.model.user import User
from app.utils.session import Session
from app.repository.interfaces.user_repository_interface import IUserRepository
from app.repository.interfaces.log_repository_interface import ILogRepository
from app.model.enums import RoleEnum
from app.service.audit_log_service import AuditLogService
from app.service.error_service import ErrorService

import hashlib
import os
import shutil
import re
from datetime import datetime

from app.service.password_service import hash_password, is_legacy_sha256_hash, verify_password


class AuthController:
    """
    Final authentication controller aligned with the new domain User model.
    """

    def __init__(
        self,
        repo: IUserRepository,
        session: Session,
        logs: ILogRepository,
        audit_log_service: AuditLogService | None = None,
        error_service: ErrorService | None = None,
    ):
        self.repo = repo
        self.session = session
        self.audit_log_service = audit_log_service or AuditLogService(logs)  # type: ignore[arg-type]
        self.error_service = error_service or ErrorService()

    def _hash(self, text: str) -> str:
        return hash_password(text)

    def _legacy_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _valid_email(self, correo):
        return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", correo) is not None

    def _normalize_dob(self, dob: str | None) -> str | None:
        if not dob:
            return None
        dob = dob.strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(dob, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        raise ValueError("Formato de fecha invalido. Use DD/MM/YYYY o YYYY-MM-DD.")

    def _log(self, action, details: str, *, actor_id: int = 1, actor_role: RoleEnum = RoleEnum.ADMIN):
        if self.session.current_user:
            actor_id = int(self.session.current_user.id)
            actor_role = self.session.current_user.role

        self.audit_log_service.log(
            actor_id=int(actor_id),
            actor_role=actor_role,
            category="AUTH",
            action=action,
            details=details,
            community_id=getattr(self.session.current_user, "community_id", None),
            target_entity_type="user",
            target_entity_id=int(actor_id),
        )

    def login(self, correo, password):
        try:
            if not correo or not password:
                return False, "Please enter both email and password.", None
            if not self._valid_email(correo):
                return False, "Invalid email format.", None

            user = self.repo.find_by_email(correo)
            if not user or not verify_password(password, user.password_hash):
                return False, "Wrong credentials. Please try again.", None

            if is_legacy_sha256_hash(user.password_hash):
                user.password_hash = self._hash(password)
                save_fn = getattr(self.repo, "save", None)
                if callable(save_fn):
                    try:
                        save_fn(user)
                    except Exception as upgrade_exc:
                        self.error_service.capture_exception(
                            upgrade_exc,
                            severity="WARN",
                            source_layer="CONTROLLER",
                            user_id=int(user.id) if user.id is not None else None,
                            community_id=user.community_id,
                            target_entity_type="user",
                            target_entity_id=int(user.id) if user.id is not None else None,
                        )

            self.session.set_current_user(user)
            self.session.current_community_id = user.community_id
            self._log(action="login_ok", details=correo, actor_id=int(user.id), actor_role=user.role)
            return True, "Login successful.", user
        except Exception as exc:
            self.error_service.capture_exception(exc, source_layer="CONTROLLER")
            return False, "Unexpected error during login.", None

    def signup(self, name: str, community_id: str, email: str, password: str, dob: str, picture_temp_path: str | None):
        try:
            if not (name and email and password and dob):
                return "Nombre, email y contrasena son campos obligatorios."
            if not self._valid_email(email):
                return "Formato de correo invalido."
            if self.repo.find_by_email(email):
                return "El correo ya esta registrado."

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
                filename = f"{hashlib.sha256(email.lower().encode('utf-8')).hexdigest()[:12]}{ext}"
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
        except Exception as exc:
            self.error_service.capture_exception(exc, source_layer="CONTROLLER")
            return "Unexpected error during signup."

    def recover_password(self, email: str):
        try:
            if not email:
                return False, "Introduce un correo."
            if not self._valid_email(email):
                return False, "Formato de correo invalido."

            user = self.repo.find_by_email(email)
            actor_id = int(user.id) if user and user.id is not None else 1
            actor_role = user.role if user else RoleEnum.ADMIN
            self._log(action="recover_request", details=email, actor_id=actor_id, actor_role=actor_role)

            if not user:
                return False, "Si el correo existe, se enviara un enlace de recuperacion."
            self.session.start_reset(user.email)
            return True, "Si el correo existe, se enviara un enlace de recuperacion."
        except Exception as exc:
            self.error_service.capture_exception(exc, source_layer="CONTROLLER")
            return False, "Unexpected error while requesting recovery."

    def update_password(self, pass1: str, pass2: str):
        try:
            if not (pass1 and pass2):
                return "Rellena ambos campos."
            if pass1 != pass2:
                return "Las contrasenas no coinciden."

            email = self.session.reset_email
            if not email:
                self._log(action="reset_attempt_no_session", details="unknown")
                return "Sesion expirada."

            user = self.repo.find_by_email(email)
            if not user:
                return "Usuario no encontrado."

            user.password_hash = self._hash(pass1)
            save_fn = getattr(self.repo, "save", None)
            if callable(save_fn):
                save_fn(user)

            self._log(action="password_changed", details=user.email, actor_id=int(user.id), actor_role=user.role)
            self.session.clear_reset()
            return "Contrasena actualizada con exito."
        except Exception as exc:
            self.error_service.capture_exception(exc, source_layer="CONTROLLER")
            return "Unexpected error updating password."

    def logout(self):
        self.session.clear()
