# app/view/edit/view_user_edit.py

import flet as ft

from app.view.base.view_base_dashboard import BaseDashboardView
from app.view.theme import (
    PRIMARY_GREEN,
    WHITE,
    INPUT_TEXT,
    INPUT_PLACEHOLDER,
    TEXT_SECONDARY,
)


class UserEditView(BaseDashboardView):
    """
    'Settings' / 'Editar perfil' screen for the logged-in user.

    It delegates the actual update to UIController.update_profile(...)
    and then shows a snackbar.
    """

    def __init__(
        self,
        page,
        controller,
        user,
        role,
        on_dashboard,
        on_settings,
        on_alerts,
        on_logout,
    ):
        self._name_field: ft.TextField | None = None
        self._email_field: ft.TextField | None = None

        super().__init__(
            page=page,
            controller=controller,
            user=user,
            role=role,
            on_settings=on_settings,
            on_dashboard=on_dashboard,
            on_alerts=on_alerts,
            on_logout=on_logout,
        )

    def build_body(self) -> ft.Control:
        # Pre-populate with current user data
        name_value = self.user.name if self.user else ""
        email_value = self.user.email if self.user else ""

        title = ft.Text(
            "Editar perfil",
            size=18,
            weight=ft.FontWeight.BOLD,
            color=PRIMARY_GREEN,
        )

        subtitle = ft.Text(
            "Actualiza tu nombre y correo electrónico.",
            size=13,
            color=TEXT_SECONDARY,
        )

        self._name_field = ft.TextField(
            label="Nombre completo",
            value=name_value,
            width=400,
            border_radius=12,
            border=ft.InputBorder.UNDERLINE,
            color=INPUT_TEXT,
            hint_text="Introduce tu nombre",
            hint_style=ft.TextStyle(color=INPUT_PLACEHOLDER),
        )

        self._email_field = ft.TextField(
            label="Correo electrónico",
            value=email_value,
            width=400,
            border_radius=12,
            border=ft.InputBorder.UNDERLINE,
            color=INPUT_TEXT,
            hint_text="Introduce tu correo",
            hint_style=ft.TextStyle(color=INPUT_PLACEHOLDER),
        )

        save_button = ft.ElevatedButton(
            text="Guardar cambios",
            on_click=self._on_save_clicked,
            width=200,
        )

        cancel_button = ft.TextButton(
            text="Cancelar",
            on_click=lambda e: self.on_dashboard(),
        )

        buttons_row = ft.Row(
            spacing=16,
            controls=[save_button, cancel_button],
        )

        return ft.Column(
            spacing=20,
            controls=[
                title,
                subtitle,
                self._name_field,
                self._email_field,
                buttons_row,
            ],
        )

    # ------------------------------------------------------------------ #
    # Handlers                                                           #
    # ------------------------------------------------------------------ #
    def _on_save_clicked(self, e):
        name = (self._name_field.value or "").strip() if self._name_field else ""
        email = (self._email_field.value or "").strip() if self._email_field else ""

        ok, msg = self.controller.update_profile(name, email)

        # Show snackbar via the page
        self.page.snack_bar = ft.SnackBar(ft.Text(msg))
        self.page.snack_bar.open = True
        self.page.update()

        if ok:
            # After a successful update, go back to dashboard
            self.on_dashboard()
