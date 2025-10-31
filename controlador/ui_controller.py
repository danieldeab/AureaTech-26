# controlador/ui_controller.py
import asyncio
import flet as ft
from vista.AlertasLoggin import (
    AlertBox, ERROR_RED, WARNING_YELL, INFO_BLUE, LIGHT_GREEN, PRIMARY_GREEN, WHITE
)

class UIController:
    def __init__(self, page: ft.Page, auth, session, assets_dir: str):
        self.page = page
        self.auth = auth
        self.session = session
        self.assets_dir = assets_dir

        # Import diferido
        from vista.views import (
            menu_view, login_view, sign_up_view, home_view,
            recover_view, reset_password_view
        )
        self._menu_view_fn = menu_view
        self._login_view_fn = login_view
        self._signup_view_fn = sign_up_view
        self._home_view_fn = home_view
        self._recover_view_fn = recover_view         # 👈 NUEVO
        self._reset_view_fn = reset_password_view    # 👈 NUEVO

    # ---------- Alertas ----------
    def show_alert(self, message: str, kind: str = "info", autohide_secs: float = 0.9):
        if kind == "error":   bg, fg = ERROR_RED, WHITE
        elif kind == "warn":  bg, fg = WARNING_YELL, PRIMARY_GREEN
        elif kind == "success": bg, fg = LIGHT_GREEN, PRIMARY_GREEN
        else:                 bg, fg = INFO_BLUE, PRIMARY_GREEN

        alert = ft.Container(
            content=AlertBox(message, bg, fg),
            alignment=ft.alignment.top_center, left=0, right=0, top=16,
        )
        self.page.overlay.append(alert)
        self.page.update()

        async def _auto_close():
            if autohide_secs and autohide_secs > 0:
                await asyncio.sleep(autohide_secs)
                if alert in self.page.overlay:
                    self.page.overlay.remove(alert)
                    await self.page.update_async()
        self.page.run_task(_auto_close)

    def clear_overlay(self):
        if self.page.overlay:
            self.page.overlay.clear()

    # ---------- Navegación ----------
    def show_menu(self, e=None):
        self.clear_overlay(); self.page.clean()
        self.page.add(self._menu_view_fn(self.assets_dir, self.on_go_login, self.on_go_signup))

    def show_login(self, e=None):
        self.clear_overlay(); self.page.clean()
        self.page.add(self._login_view_fn(self.assets_dir, self.on_back_menu, self.on_login_submit, self.on_go_signup, self.on_go_recover))

    def show_signup(self, e=None):
        self.clear_overlay(); self.page.clean()
        self.page.add(self._signup_view_fn(self.assets_dir, self.on_back_menu, self.on_signup_submit, self.on_go_login))

    def show_home(self, e=None):
        self.clear_overlay(); self.page.clean()
        name = self.session.current_user.display_name if self.session.current_user else "Usuario"
        self.page.add(self._home_view_fn(self.assets_dir, name, self.on_logout))

    # ✅ NUEVAS VISTAS
    def show_recover(self, e=None):
        self.clear_overlay(); self.page.clean()
        self.page.add(self._recover_view_fn(self.assets_dir, self.on_back_menu, self.on_recover_submit, self.on_go_login))

    def show_reset(self, email: str):
        self.clear_overlay(); self.page.clean()
        self.page.add(self._reset_view_fn(self.assets_dir, email, self.on_back_menu, self.on_reset_submit))

    # ---------- Callbacks ----------
    def on_go_login(self, e=None):  self.show_login()
    def on_go_signup(self, e=None): self.show_signup()
    def on_go_recover(self, e=None): self.show_recover()
    def on_back_menu(self, e=None):
        self.show_alert("Volviendo al menú principal...", "info"); self.show_menu()

    def on_login_submit(self, email: str, password: str):
        ok, msg = self.auth.login((email or "").strip(), (password or "").strip())
        if ok:
            self.show_alert(msg, "success")
            async def _go_home():
                await asyncio.sleep(0.8); self.clear_overlay(); self.show_home()
            self.page.run_task(_go_home)
        else:
            self.show_alert(msg, "error" if "error" in msg.lower() else "warn")

    def on_signup_submit(self, fullname: str, email: str, password: str, dob: str | None = None):
        if not fullname or not email or not password:
            self.show_alert("Completa nombre, email y contraseña.", "warn"); return
        ok, msg = self.auth.repo.add_user(email=email, password=password, display_name=fullname)
        if ok:
            self.show_alert("Cuenta creada con éxito. Inicia sesión.", "success")
            async def _go_login():
                await asyncio.sleep(0.8); self.clear_overlay(); self.show_login()
            self.page.run_task(_go_login)
        else:
            self.show_alert(msg, "error")

    # ✅ RECUPERACIÓN
    def on_recover_submit(self, email: str):
        email = (email or "").strip().lower()
        if not email:
            self.show_alert("Ingresá tu correo.", "warn"); return
        if not self.auth.repo.find_by_email(email):
            # por seguridad, respondemos igual
            self.show_alert("Si el correo existe, te enviamos un enlace (simulado).", "info")
        else:
            self.show_alert("Enlace de recuperación enviado (simulado).", "success")
        async def _go_reset():
            await asyncio.sleep(0.8); self.clear_overlay(); self.show_reset(email)
        self.page.run_task(_go_reset)

    def on_reset_submit(self, email: str, pwd: str, confirm: str):
        if not pwd or not confirm:
            self.show_alert("Completá ambos campos.", "warn"); return
        if len(pwd) < 6:
            self.show_alert("La contraseña debe tener al menos 6 caracteres.", "warn"); return
        if pwd != confirm:
            self.show_alert("Las contraseñas no coinciden.", "error"); return
        ok, msg = self.auth.repo.update_password(email, pwd)
        if ok:
            self.show_alert("Contraseña actualizada. Inicia sesión.", "success")
            async def _go_login():
                await asyncio.sleep(0.8); self.clear_overlay(); self.show_login()
            self.page.run_task(_go_login)
        else:
            self.show_alert(msg, "error")

    def on_logout(self, e=None):
        self.auth.logout(); self.show_alert("Sesión cerrada.", "success"); self.show_menu()
