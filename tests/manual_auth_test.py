# tests/manual_auth_test.py

import os, sys

# Add project root to Python path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import flet as ft

from app.view.auth.view_login import LoginView
from app.view.auth.view_signup import SignupView
from app.view.auth.view_menu import MenuView
from app.view.auth.view_recover import RecoverPasswordView
from app.view.auth.view_reset_password import ResetPasswordView

# ================================================================
# Dummy Controller for Manual Testing
# ================================================================
class DummyAuthController:
    def __init__(self, page):
        self.page = page
        self.history = []     # true stack for navigation

    # ======================================================
    # Internal utilities
    # ======================================================
    def _push(self, name, view):
        """Push a new screen, without duplicating the last entry."""
        if not self.history or self.history[-1] != name:
            self.history.append(name)        
            
        self.page.controls.clear()
        self.page.add(view)
        self.page.update()

    def _replace(self, name, view):
        """Replace the current screen."""
        if self.history:
            self.history[-1] = name
        else:
            self.history.append(name)

        self.page.controls.clear()
        self.page.add(view)
        self.page.update()

    # ======================================================
    # Screens
    # ======================================================
    def show_menu(self):
        view = MenuView(self.page, controller=self)
        self._push("menu", view)

    def show_login(self):
        view = LoginView(
            self.page,
            controller=self,
            on_back_click=self.go_back
        )
        self._push("login", view)


    def show_signup(self):
        view = SignupView(
            self.page,
            controller=self,
            on_back_click=self.go_back
        )
        self._push("signup", view)

    def show_dashboard(self):
        dummy = ft.Container(
            width=600, height=300,
            bgcolor="#2D4A46",
            border_radius=20,
            alignment=ft.alignment.center,
            content=ft.Text("DASHBOARD (dummy)", color="white", size=26),
        )
        self._push("dashboard", dummy)

    def show_recover(self):
        view = RecoverPasswordView(
            self.page,
            controller=self,
            on_back_click=self.go_back
        )
        self._push("recover", view)

    def show_reset(self):
        view = ResetPasswordView(
            self.page,
            controller=self,
            on_back_click=self.go_back
        )
        self._push("reset", view)

    # ======================================================
    # View Callbacks
    # ======================================================
    def login(self, email, password):
        # simulate login success
        self.show_dashboard()

    def signup(self, fullname, email, password, dob, picture_path=None):
        # simulate email exists check
        if email.lower().startswith("exists"):
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Email already exists (simulated)"), bgcolor="#B00020"
            )
            self.page.snack_bar.open = True
            self.page.update()
            return

        # signup success → ALWAYS go to login
        view = LoginView(
            self.page,
            controller=self,
            on_back_click=self.go_back
        )
        self._replace("login", view)

        self.page.snack_bar = ft.SnackBar(
            ft.Text("Account created. Please log in."), bgcolor="#2E7D32"
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def reset_password(self, pass1, pass2):
        if pass1 != pass2:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Las contraseñas no coinciden."), bgcolor="#B00020"

            )
        else:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Contraseña restablecida con éxito."), bgcolor="#2E7D32"
            )
            self._replace("login", LoginView(self.page, self, on_back_click=self.go_back))
        
        self.page.snack_bar.open = True
        self.page.update()

    def recover(self, email):
        #Simulate successful email check
        self.page.snack_bar = ft.SnackBar(
            ft.Text("Si el correo existe, se ha enviado un enlace de recuperación (simulado). Redirigiendo..."),
            bgcolor="#2E7D32"
        )
        self.page.snack_bar.open = True
        self.page.update()

        # Now move to reset password view
        self.show_reset()

    def go_login(self):
        self.show_login()

    def go_signup(self):
        self.show_signup()

    def go_recover(self):
        self.show_recover()

    def go_reset(self):
        self.show_reset()

    # ======================================================
    # Back button logic
    # ======================================================
    def _dummy_dashboard(self):
        return ft.Container(
            width=600, height=300,
            bgcolor="#2D4A46",
            border_radius=20,
            alignment=ft.alignment.center,
            content=ft.Text("DASHBOARD (dummy)", color="white", size=26),
        )

    def go_back(self):       
        if not self.history:
            return # nothing to go back to
        # Remove the current screen
        self.history.pop()

        if not self.history:
            # No history left, go to menu
            return self._replace("menu", MenuView(self.page, self))

        # The new current screen (after popping)
        last = self.history[-1]

        # Now RENDER WITHOUT PUSHING ANYTHING
        if last == "menu":
            self._replace("menu", MenuView(self.page, self))
        elif last == "login":
            self._replace("login", LoginView(self.page, self, on_back_click=self.go_back))
        elif last == "signup":
            self._replace("signup", SignupView(self.page, self, on_back_click=self.go_back))
        elif last == "recover":
            self._replace("recover", RecoverPasswordView(self.page, self, on_back_click=self.go_back))
        elif last == "dashboard":
            self._replace("dashboard", self._dummy_dashboard())
        elif last == "reset":
            self._replace("reset", ResetPasswordView(self.page, self, on_back_click=self.go_back))

# ================================================================
# Flet Testing App
# ================================================================
def main(page: ft.Page):
    page.title = "AureaTech Auth Views — Visual Test"
    page.window_width = 1100
    page.window_height = 750
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    page.assets_dir = "app/assets"

    controller = DummyAuthController(page)
    controller.show_menu()


if __name__ == "__main__":
    ft.app(target=main)
