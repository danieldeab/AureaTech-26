import flet as ft

from app.controller.auth_controller import AuthController, Session
from app.view.auth.view_login import LoginView
from app.view.auth.view_signup import SignupView
from app.view.auth.view_menu import MenuView
from app.view.auth.view_recover import RecoverPasswordView
from app.view.auth.view_reset_password import ResetPasswordView
from app.view.dashboard.view_user_dashboard import UserDashboardView
from app.view.theme import (
    SUCCESS_GREEN,
    ERROR_RED,
)

# Dashboard imports will be added once dashboard migration is complete
# from app.view.dashboard.main_dashboard import MainDashboardView
# from app.view.admin.admin_dashboard import AdminDashboardView
# ...


class UIController:
    """
    Final UI Controller integrating:
      - Authentication flow (Menu → Login → Signup → Recover → Reset)
      - Navigation stack for back-navigation
      - AuthController for authentication logic

    Responsibilities according to the class diagram:
      - Navigation between all views
      - Delegation of login/signup/reset to AuthController
      - Global user session and role handling
    """

    def __init__(self, page: ft.Page, auth_controller: AuthController, session: Session):
        self.page = page
        self.auth = auth_controller
        self.session = session

        self.history = []             # navigation stack
        self.page.assets_dir = "app/assets"

    # ======================================================
    # Internal navigation utilities
    # ======================================================
    def _push(self, name: str, view:  ft.UserControl):
        if not self.history or self.history[-1] != name:
            self.history.append(name)

        self.page.controls.clear()
        self.page.add(view)
        self.page.update()

    def _replace(self, name: str, view:  ft.UserControl):
        if self.history:
            self.history[-1] = name
        else:
            self.history.append(name)

        self.page.controls.clear()
        self.page.add(view)
        self.page.update()

    def _notify(self, msg):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg))
        self.page.snack_bar.open = True
        self.page.update()


    # ======================================================
    # Screens
    # ======================================================
    def show_menu(self):
        self._push("menu", MenuView(self.page, self))

    def show_login(self):
        self._push("login", LoginView(self.page, controller=self, on_back_click=self.go_back))

    def show_signup(self):
        self._push("signup", SignupView(self.page, controller=self, on_back_click=self.go_back))

    def show_recover(self):
        self._push("recover", RecoverPasswordView(self.page, controller=self, on_back_click=self.go_back))

    def show_reset(self):
        self._push("reset", ResetPasswordView(self.page, controller=self, on_back_click=self.go_back))

    # ======================================================
    # Post-authentication navigation
    # ======================================================
    def show_dashboard(self, e=None):
        user = self.session.current_user
        if not user:
            return self.show_login()

        role = user.role.lower()

        if role == "vecino":
            return self.show_user_dashboard()
        elif role == "admin":
            return self.show_admin_dashboard()
        elif role == "tecnico":
            return self.show_tecnico_dashboard()
        
    def show_user_dashboard(self, e=None):
        user = self.session.current_user

        view = UserDashboardView(
            page=self.page,
            controller=self,
            user=user,
            role="vecino",

            # nav buttons
            on_settings=self.show_settings,
            on_alerts=self.show_alerts,
            on_dashboard=self.show_user_dashboard,
            on_logout=self.logout,
        )

        self.history = ["dashboard"]
        self._replace("dashboard", view)
    
    def show_alerts(self, e=None):
        self._replace(
            "alerts",
            ft.Column(
                controls=[
                    ft.Text("No alerts available.", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("This view will show sensor alerts later."),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        )

    def show_settings(self, e=None):
        self._replace(
            "settings",
            ft.Column(
                controls=[
                    ft.Text("Settings view.", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("This view will allow changing user settings later."),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        )

    # ======================================================
    # View Callbacks (delegations to AuthController)
    # ======================================================
    def login(self, email, password):
        ok, msg, user = self.auth.login(email, password)
        self._notify(msg)

        if not ok:
            return
        else:
            # Successful login → dashboard
            return self.show_dashboard()


    def signup(self, name, email, password, dob, picture_path=None):
        
        result = self.auth.signup(
            name=name, 
            email=email,
            password=password, 
            dob=dob, 
            picture_temp_path=picture_path
        )

        if result is True:
            # Signup success → Login
            self._replace("login", LoginView(self.page, self, on_back_click=self.go_back))

            self.page.snack_bar = ft.SnackBar(
                ft.Text("Cuenta creada con éxito. Inicia sesión."),
                bgcolor=SUCCESS_GREEN
            )
            self.page.snack_bar.open = True
            self.page.update()
            return

        # Signup failed
        self.page.snack_bar = ft.SnackBar(
            ft.Text(result or "Error al registrarse."), 
            bgcolor=ERROR_RED
        )
        self.page.snack_bar.open = True
        self.page.update()

    def recover(self, email):
        result = self.auth.recover_password(email)

        # Show snackbar
        self.page.snack_bar = ft.SnackBar(
            ft.Text(result),
            bgcolor=SUCCESS_GREEN if result.startswith("Si el correo") else ERROR_RED,
        )
        self.page.snack_bar.open = True
        self.page.update()

        # Only navigate to reset on successful request
        if result.startswith("Si el correo"):
            self.show_reset()


    def reset_password(self, pass1, pass2):
        result = self.auth.update_password(pass1, pass2)

        color = SUCCESS_GREEN if "éxito" in result.lower() else ERROR_RED
        self.page.snack_bar = ft.SnackBar(ft.Text(result), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()

        if "éxito" in result.lower():
            self.history = ["login"]
            self._replace("login", LoginView(self.page, self, on_back_click=self.go_back))    

    def logout(self, e=None):
        self.session.clear()
        self.show_login()

    # ======================================================
    # Navigation callbacks from views
    # ======================================================
    def go_login(self): self.show_login()
    def go_signup(self): self.show_signup()
    def go_recover(self): self.show_recover()
    def go_reset(self): self.show_reset()

    # ======================================================
    # BACK navigation
    # ======================================================
    def go_back(self):
        if not self.history:
            return

        self.history.pop()

        if not self.history:
            return self._replace("menu", MenuView(self.page, self))

        last = self.history[-1]

        if last == "menu":
            self._replace("menu", MenuView(self.page, self))
        elif last == "login":
            self._replace("login", LoginView(self.page, self, on_back_click=self.go_back))
        elif last == "signup":
            self._replace("signup", SignupView(self.page, self, on_back_click=self.go_back))
        elif last == "recover":
            self._replace("recover", RecoverPasswordView(self.page, self, on_back_click=self.go_back))
        elif last == "reset":
            self._replace("reset", ResetPasswordView(self.page, self, on_back_click=self.go_back))
        elif last == "dashboard":
            self.show_dashboard()
