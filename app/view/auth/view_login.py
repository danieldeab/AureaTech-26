import flet as ft
from app.view.theme import (
    PRIMARY_GREEN,
    LIGHT_GREY,
    WHITE,
    BACK_BLUE,
    FULL_BLACK,
    TEXT_SECONDARY,
    BRAND_ACCENT_BLUE,
    INPUT_PLACEHOLDER,
    INPUT_TEXT,
)
from app.view.base.view_base_auth import ViewBaseAuth


class LoginView(ViewBaseAuth):
    """
    Login screen.

    Controller must expose:
      - controller.login(email, password)
      - controller.go_back()
      - controller.go_signup()
      - controller.go_recover()
    """

    def __init__(self, page: ft.Page, controller, on_back_click=None):
        # Base auth view sets up card, title, back button, etc.
        super().__init__(
            page=page,
            controller=controller,
            title="Log In",
            subtitle="",
            show_back=True,
        )
        # Keep backwards compatibility with optional custom back handler
        self.on_back_click = on_back_click or controller.go_back

        # Fields are created in build_body()
        self.email_field: ft.TextField | None = None
        self.password_field: ft.TextField | None = None

    # Optional override: use the per-view back handler if provided
    def _make_back_button(self):
        back_icon = ft.Image(
            src=f"{self.page.assets_dir}/back.png",
            width=26,
            height=26,
            error_content=ft.Text(
                "<",
                color=BACK_BLUE,
                size=26,
                weight=ft.FontWeight.BOLD,
            ),
        )
        return ft.GestureDetector(
            on_tap=lambda e: (
                print("Back clicked login"),
                self.on_back_click(),
            ),
            content=ft.Container(padding=6, content=back_icon),
        )

    # Child-specific content goes here
    def build_body(self) -> ft.Control:
        FIELD_W = 460
        FONT_SIZE_LABEL = 14
        FIELD_SPACE = 10

        # --- Text Fields (stored for the controller) ---
        self.email_field = ft.TextField(
            label="Email",
            label_style=ft.TextStyle(color=PRIMARY_GREEN),
            hint_text="example@example.com",
            width=FIELD_W,
            bgcolor=LIGHT_GREY,
            border_radius=12,
            border=ft.InputBorder.NONE,
            content_padding=ft.padding.symmetric(12, 14),
            color=INPUT_TEXT,
            hint_style=ft.TextStyle(color=INPUT_PLACEHOLDER),
            on_submit=lambda e: self.password_field.focus(),
        )

        self.password_field = ft.TextField(
            label="Contraseña",
            label_style=ft.TextStyle(color=PRIMARY_GREEN),
            hint_text="Contraseña",
            password=True,
            can_reveal_password=True,
            width=FIELD_W,
            bgcolor=LIGHT_GREY,
            border_radius=12,
            border=ft.InputBorder.NONE,
            content_padding=ft.padding.symmetric(12, 14),
            color=INPUT_TEXT,
            hint_style=ft.TextStyle(color=INPUT_PLACEHOLDER),
            on_submit=lambda e: _submit(),
        )

        # --- Submit handler ---
        def _submit(e=None):
            self.controller.login(
                self.email_field.value,
                self.password_field.value,
            )

        login_cta = ft.ElevatedButton(
            "Log In",
            width=260,
            height=48,
            bgcolor=PRIMARY_GREEN,
            color=WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=24)
            ),
            on_click=_submit,
        )

        # --- "Forget password" link ---
        forget_row = ft.Row(
            controls=[
                ft.TextButton(
                    "Forget Password",
                    style=ft.ButtonStyle(color=BACK_BLUE),
                    on_click=lambda e: self.controller.go_recover(),
                )
            ],
            alignment=ft.MainAxisAlignment.END,
            width=FIELD_W,
        )

        # --- Footer ("Don't have an account?") ---
        footer_row = ft.Row(
            controls=[
                ft.Text("Don't have an account? ", color=TEXT_SECONDARY),
                ft.TextButton(
                    "Sign Up",
                    style=ft.ButtonStyle(color=BRAND_ACCENT_BLUE),
                    on_click=lambda e: self.controller.go_signup(),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        # --- Form Layout (inside the auth card provided by ViewBaseAuth) ---
        return ft.Column(
            controls=[
                ft.Text(
                    "Email",
                    color=PRIMARY_GREEN,
                    size=FONT_SIZE_LABEL,
                ),
                self.email_field,
                ft.Container(height=FIELD_SPACE),

                ft.Text(
                    "Contraseña",
                    color=PRIMARY_GREEN,
                    size=FONT_SIZE_LABEL,
                ),
                self.password_field,
                ft.Container(height=6),

                forget_row,
                ft.Container(height=14),

                login_cta,
                ft.Container(height=6),

                footer_row,
            ],
            spacing=6,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
