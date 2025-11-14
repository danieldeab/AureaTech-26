# auth_controller.py
from app.models.auth_service import AuthService, write_log

class AuthController:
    def __init__(self, view):
        self.service = AuthService()
        self.view = view

    def login(self, correo, password):
        ok, msg = self.service.autenticar(correo, password)
        self.view.notificar(msg)
        if not ok and "agotados" in msg:
            self.view.mostrar_recuperacion()
        write_log("login_ok", correo, getattr(self.service.user, "rol", "vecino"))


    def registrar(self, usuario, correo, password):
        ok, msg = self.service.registrar(usuario, correo, password)
        self.view.notificar(msg)
        if ok:
            self.view.mostrar_login()

    def recuperar(self, correo):
        ok, msg = self.service.recuperar(correo)
        self.view.notificar(msg)
        self.view.mostrar_login()
