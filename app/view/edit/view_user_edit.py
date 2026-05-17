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
        plates: list[dict] | None = None,
    ):
        self._name_field: ft.TextField | None = None
        self._email_field: ft.TextField | None = None
        self._plate_field: ft.TextField | None = None
        self.plates = plates or []

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

        self._plate_field = ft.TextField(
            label="Nueva matricula",
            width=260,
            border_radius=12,
            border=ft.InputBorder.UNDERLINE,
            color=INPUT_TEXT,
            hint_text="1234 ABC",
            hint_style=ft.TextStyle(color=INPUT_PLACEHOLDER),
        )

        plate_rows: list[ft.Control] = []
        for plate in self.plates:
            status = plate.get("status") or ("APPROVED" if plate.get("is_active") else "PENDING")
            plate_id = plate.get("allowed_plate_id")
            row_controls: list[ft.Control] = [
                ft.Text(str(plate.get("plate", "--")), width=120, color=PRIMARY_GREEN, weight=ft.FontWeight.BOLD),
                ft.Text(str(status), width=100, color=TEXT_SECONDARY),
            ]
            if plate_id is not None:
                row_controls.append(
                    ft.TextButton(
                        text="Desactivar",
                        on_click=lambda e, pid=plate_id: self._on_deactivate_plate(pid),
                    )
                )
            plate_rows.append(ft.Row(spacing=10, controls=row_controls))

        plates_section = ft.Container(
            bgcolor=WHITE,
            border_radius=10,
            padding=12,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Text("Matriculas registradas", size=16, weight=ft.FontWeight.BOLD, color=PRIMARY_GREEN),
                    ft.Text("Las nuevas matriculas quedan pendientes hasta que las apruebe un tecnico o administrador.", size=12, color=TEXT_SECONDARY),
                    *(plate_rows or [ft.Text("No hay matriculas registradas.", size=12, color=TEXT_SECONDARY)]),
                    ft.Row(
                        spacing=10,
                        controls=[
                            self._plate_field,
                            ft.ElevatedButton(text="Solicitar alta", on_click=self._on_add_plate),
                        ],
                    ),
                ],
            ),
        )

        return ft.Column(
            spacing=20,
            controls=[
                title,
                subtitle,
                self._name_field,
                self._email_field,
                buttons_row,
                plates_section,
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

    def _on_add_plate(self, e):
        plate = (self._plate_field.value or "").strip() if self._plate_field else ""
        ok, msg = self.controller.request_plate_registration(plate)
        self.page.snack_bar = ft.SnackBar(ft.Text(msg))
        self.page.snack_bar.open = True
        self.page.update()
        if ok:
            self.on_settings()

    def _on_deactivate_plate(self, allowed_plate_id: int):
        ok, msg = self.controller.deactivate_plate_registration(allowed_plate_id)
        self.page.snack_bar = ft.SnackBar(ft.Text(msg))
        self.page.snack_bar.open = True
        self.page.update()
        if ok:
            self.on_settings()
