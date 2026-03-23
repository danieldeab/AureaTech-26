# app/view/auth/view_recover.py

import os
import flet as ft
from app.view.base.view_base_auth import ViewBaseAuth
from app.view.theme import (
    PRIMARY_GREEN, LIGHT_GREY, WHITE, BACK_BLUE,
    BORDER_SOFT, PANEL_W, PANEL_H, FULL_BLACK, TEXT_SECONDARY
)


class RecoverPasswordView(ViewBaseAuth):
    """
    View for entering email to recover password.
    """

    def __init__(self, page: ft.Page, controller, on_back_click=None):
        super().__init__(
            page=page,
            controller=controller,
            title="Recover Account",
            subtitle="Enter your email to receive a reset link",
            show_back=True,
        )

        self.on_back_click = on_back_click or controller.go_back
        self.email_field = None

    # override back button according to Login/Signup style
    def _make_back_button(self):
        back_icon = ft.Image(
            src=f"{self.page.assets_dir}/back.png",
            width=26,
            height=26,
            error_content=ft.Text("<", color=BACK_BLUE, size=26, weight=ft.FontWeight.BOLD),
        )
        return ft.GestureDetector(
            on_tap=lambda e: self.on_back_click(),
            content=ft.Container(padding=6, content=back_icon),
        )

    # MAIN UI BODY
    def build_body(self) -> ft.Control:
        FIELD_W = 460
        FONT_SIZE_LABEL = 14

        # Email field
        self.email_field = ft.TextField(
            label="Email",
            label_style=ft.TextStyle(color=PRIMARY_GREEN),
            hint_text="example@example.com",
            width=FIELD_W,
            bgcolor=LIGHT_GREY,
            border_radius=12,
            border=ft.InputBorder.NONE,
            content_padding=ft.padding.symmetric(12, 14),
            color=FULL_BLACK,
            hint_style=ft.TextStyle(color="#666666"),
            on_submit=lambda e: self._submit(),
        )

        send_btn = ft.ElevatedButton(
            "Send reset link",
            width=260,
            height=48,
            bgcolor=PRIMARY_GREEN,
            color=WHITE,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=24)),
            on_click=lambda e: self._submit(),
        )

        footer_row = ft.Row(
            controls=[
                ft.Text("Remembered your password? ", color=TEXT_SECONDARY),
                ft.TextButton(
                    "Log in",
                    on_click=lambda e: self.controller.go_login(),
                    style=ft.ButtonStyle(color=BACK_BLUE),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        return ft.Column(
            controls=[
                ft.Text("Email", size=FONT_SIZE_LABEL, color=PRIMARY_GREEN),
                self.email_field,
                ft.Container(height=20),
                send_btn,
                ft.Container(height=20),
                footer_row,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _submit(self):
        email = self.email_field.value
        self.controller.recover(email)
