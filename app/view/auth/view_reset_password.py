# app/view/auth/view_reset_password.py

import os
import flet as ft
from app.view.base.view_base_auth import ViewBaseAuth
from app.view.theme import (
    PRIMARY_GREEN, LIGHT_GREY, WHITE, BACK_BLUE,
    BORDER_SOFT, PANEL_W, PANEL_H, FULL_BLACK, TEXT_SECONDARY
)


class ResetPasswordView(ViewBaseAuth):
    """
    Reset password screen.
    """

    def __init__(self, page: ft.Page, controller, on_back_click=None):
        super().__init__(
            page=page,
            controller=controller,
            title="Reset Password",
            subtitle="Enter your new password",
            show_back=True,
        )

        self.on_back_click = on_back_click or controller.go_back
        self.new_pass_field = None
        self.confirm_pass_field = None

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

    def build_body(self) -> ft.Control:
        FIELD_W = 460
        FONT_SIZE_LABEL = 14

        self.new_pass_field = ft.TextField(
            label="New password",
            label_style=ft.TextStyle(color=PRIMARY_GREEN),
            password=True,
            can_reveal_password=True,
            width=FIELD_W,
            bgcolor=LIGHT_GREY,
            border_radius=12,
            border=ft.InputBorder.NONE,
            content_padding=ft.padding.symmetric(12, 14),
            color=FULL_BLACK,
            hint_style=ft.TextStyle(color="#666666"),
            on_submit=lambda e: self.confirm_pass_field.focus(),
        )

        self.confirm_pass_field = ft.TextField(
            label="Confirm password",
            label_style=ft.TextStyle(color=PRIMARY_GREEN),
            password=True,
            can_reveal_password=True,
            width=FIELD_W,
            bgcolor=LIGHT_GREY,
            border_radius=12,
            border=ft.InputBorder.NONE,
            content_padding=ft.padding.symmetric(12, 14),
            color=FULL_BLACK,
            hint_style=ft.TextStyle(color="#666666"),
            on_submit=lambda e: self._submit(),
        )

        reset_btn = ft.ElevatedButton(
            "Reset password",
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
                    style=ft.ButtonStyle(color=BACK_BLUE),
                    on_click=lambda e: self.controller.go_login(),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        return ft.Column(
            controls=[
                ft.Text("New password", size=FONT_SIZE_LABEL, color=PRIMARY_GREEN),
                self.new_pass_field,
                ft.Container(height=20),

                ft.Text("Confirm password", size=FONT_SIZE_LABEL, color=PRIMARY_GREEN),
                self.confirm_pass_field,
                ft.Container(height=20),

                reset_btn,
                ft.Container(height=20),

                footer_row,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _submit(self):
        self.controller.reset_password(
            self.new_pass_field.value,
            self.confirm_pass_field.value
        )
