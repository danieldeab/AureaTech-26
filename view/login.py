# login.py
import flet as ft
from control.auth_controller import AuthController

class LoginView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.controller = AuthController(self)

        self.page.title = "Login / Registro - Minimal"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.bgcolor = "#f4f4f4"

        self._construir_vistas()
        self.contenedor = ft.Column([self.login_view], alignment=ft.MainAxisAlignment.CENTER)
        self.page.add(self.contenedor)

    def _construir_vistas(self):
        # Login
        self.correo_input = ft.TextField(label="Correo Electrónico", width=250)
        self.pass_input = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=250)
        login_btn = ft.ElevatedButton("Iniciar sesión", on_click=self._login_click, width=250)
        switch_to_register = ft.TextButton("¿No tienes cuenta? Regístrate", on_click=self.mostrar_registro)
        self.login_view = ft.Column(
            [
                ft.Text("Iniciar Sesión", size=25, weight=ft.FontWeight.BOLD),
                self.correo_input,
                self.pass_input,
                login_btn,
                switch_to_register
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        # Registro
        self.reg_user = ft.TextField(label="Usuario", width=250)
        self.reg_email = ft.TextField(label="Correo electrónico", width=250)
        self.reg_pass = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=250)
        reg_btn = ft.ElevatedButton("Crear cuenta", on_click=self._registrar_click, width=250)
        switch_to_login = ft.TextButton("¿Ya tienes cuenta? Inicia sesión", on_click=self.mostrar_login)
        self.register_view = ft.Column(
            [
                ft.Text("Crear Cuenta", size=25, weight=ft.FontWeight.BOLD),
                self.reg_user,
                self.reg_email,
                self.reg_pass,
                reg_btn,
                switch_to_login
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        # Recuperación
        self.recovery_email = ft.TextField(label="Correo electrónico", width=250)
        send_recovery_btn = ft.ElevatedButton("Enviar enlace de recuperación", on_click=self._enviar_recuperacion, width=250)
        switch_to_login_from_recovery = ft.TextButton("Volver al login", on_click=self.mostrar_login)
        self.recovery_view = ft.Column(
            [
                ft.Text("Recuperar Contraseña", size=25, weight=ft.FontWeight.BOLD),
                self.recovery_email,
                send_recovery_btn,
                switch_to_login_from_recovery
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

    # Funciones de vista
    def mostrar_login(self, e=None):
        self.contenedor.controls.clear()
        self.contenedor.controls.append(self.login_view)
        self.page.update()

    def mostrar_registro(self, e=None):
        self.contenedor.controls.clear()
        self.contenedor.controls.append(self.register_view)
        self.page.update()

    def mostrar_recuperacion(self, e=None):
        self.contenedor.controls.clear()
        self.contenedor.controls.append(self.recovery_view)
        self.page.update()

    def notificar(self, mensaje):
        self.page.snack_bar = ft.SnackBar(ft.Text(mensaje))
        self.page.snack_bar.open = True
        self.page.update()

    # Eventos
    def _login_click(self, e):
        self.controller.login(self.correo_input.value.strip(), self.pass_input.value.strip())

    def _registrar_click(self, e):
        self.controller.registrar(self.reg_user.value.strip(), self.reg_email.value.strip(), self.reg_pass.value.strip())

    def _enviar_recuperacion(self, e):
        self.controller.recuperar(self.recovery_email.value.strip())


def main(page: ft.Page):
    LoginView(page)

if __name__ == "__main__":
    ft.app(target=main)
