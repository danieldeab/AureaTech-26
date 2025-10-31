# controlador/ui_controller.py
import os
import asyncio
import flet as ft
from vista.AlertasLoggin import (
    AlertBox,
    ERROR_RED, WARNING_YELL, INFO_BLUE, LIGHT_GREEN, PRIMARY_GREEN, WHITE
)

class UIController:
    def __init__(self, page: ft.Page, auth, session, assets_dir: str):
        self.page = page
        self.auth = auth
        self.session = session
        self.assets_dir = assets_dir

        # Import diferido para evitar ciclos
        from vista.views import menu_view, login_view, home_view
        self._menu_view_fn = menu_view
        self._login_view_fn = login_view
        self._home_view_fn = home_view

    # ---------- Alertas ----------
    def show_alert(self, message: str, kind: str = "info", autohide_secs: float = 0.9):
        if kind == "error":
            bg, fg = ERROR_RED, WHITE
        elif kind == "warn":
            bg, fg = WARNING_YELL, PRIMARY_GREEN
        elif kind == "success":
            bg, fg = LIGHT_GREEN, PRIMARY_GREEN
        else:
            bg, fg = INFO_BLUE, PRIMARY_GREEN

        alert = ft.Container(
            content=AlertBox(message, bg, fg),
            alignment=ft.alignment.top_center,
            left=0, right=0, top=16,
        )
        self.page.overlay.append(alert)
        self.page.update()

        async def _auto_close():
            if autohide_secs and autohide_secs > 0:
                await asyncio.sleep(autohide_secs)
                if alert in self.page.overlay:
                    self.page.overlay.remove(alert)
                    await self.page.update_async()

        # 👈 pasar la función, NO llamarla
        self.page.run_task(_auto_close)

    def clear_overlay(self):
        if self.page.overlay:
            self.page.overlay.clear()

    # ---------- Callbacks de UI ----------
    def on_go_login(self, e=None):
        self.clear_overlay()
        self.page.clean()
        self.page.add(
            self._login_view_fn(self.assets_dir, self.on_back_menu, self.on_login_submit)
        )

    def on_back_menu(self, e=None):
        self.show_alert("Volviendo al menú principal...", "info")
        self.show_menu()

    def on_login_submit(self, email: str, password: str):
        email = (email or "").strip()
        password = (password or "").strip()

        ok, msg = self.auth.login(email, password)
        if ok:
            self.show_alert(msg, "success")

            async def _go_home():
                await asyncio.sleep(0.8)
                self.clear_overlay()
                self.show_home()

            # 👈 pasar la función, NO llamarla
            self.page.run_task(_go_home)
        else:
            kind = "warn" if "vacíos" in msg.lower() else "error"
            self.show_alert(msg, kind)

    def on_logout(self, e=None):
        self.auth.logout()
        self.show_alert("Sesión cerrada.", "success")
        self.show_menu()

    # ---------- Navegación de pantallas ----------
    def show_menu(self, e=None):
        self.clear_overlay()
        self.page.clean()
        self.page.add(self._menu_view_fn(self.assets_dir, self.on_go_login))

    def show_home(self, e=None):
        self.clear_overlay()
        self.page.clean()
        self.page.add(
            self._home_view_fn(
                self.assets_dir,
                self.session.current_user.display_name if self.session.current_user else "Usuario",
                self.on_logout,
            )
        )
