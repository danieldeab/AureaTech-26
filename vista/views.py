# vista/views.py
import os
import flet as ft

LIGHT_LILAC = "#E9EDFF"
PRIMARY_GREEN = "#2D4A46"
WHITE = "#FFFFFF"
BORDER_SOFT = "#00000014"
BACK_BLUE = "#3F66FF"
PANEL_W = 980
PANEL_H = 640

# ---------- VISTA: MENÚ PRINCIPAL ----------
def menu_view(assets_dir: str, on_login_click):
    bottom_h = int(PANEL_H * 0.18)

    logo = ft.Image(
        src=os.path.join(assets_dir, "logo.png"),
        width=220, height=220,
        fit=ft.ImageFit.CONTAIN,
        error_content=ft.Text("No se encontró 'logo.png'", color="red"),
    )
    btn_login = ft.ElevatedButton(
        "Login", width=300, height=52,
        bgcolor=LIGHT_LILAC, color=PRIMARY_GREEN,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=26)),
        on_click=on_login_click,
    )
    btn_signup = ft.ElevatedButton(
        "Sign Up", width=300, height=52,
        bgcolor=PRIMARY_GREEN, color=WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=26)),
    )

    content = ft.Container(
        alignment=ft.alignment.center, expand=True,
        content=ft.Column(
            [logo, btn_login, btn_signup],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        ),
    )

    return ft.Container(
        width=PANEL_W, height=PANEL_H,
        bgcolor=WHITE, border_radius=22,
        border=ft.border.all(1, BORDER_SOFT),
        content=ft.Stack(controls=[
            ft.Container(  # Sol arriba izq
                content=ft.Image(
                    src=os.path.join(assets_dir, "sol.png"),
                    width=140, fit=ft.ImageFit.CONTAIN,
                    error_content=ft.Text("No se encontró 'sol.png'", color="red"),
                ),
                left=8, top=8,
            ),
            ft.Container(  # Franja inferior
                bottom=0, left=0, right=0,
                content=ft.Image(
                    src=os.path.join(assets_dir, "parte_inferior.png"),
                    width=PANEL_W, height=bottom_h, fit=ft.ImageFit.COVER,
                    error_content=ft.Text("No se encontró 'parte_inferior.png'", color="red"),
                ),
            ),
            content,
        ]),
    )

# ---------- VISTA: LOGIN ----------
def login_view(assets_dir: str, on_back, on_submit):
    email = ft.TextField(
        label="Email", hint_text="example@example.com", width=520,
        bgcolor=LIGHT_LILAC, border_radius=14, border=ft.InputBorder.NONE,
        content_padding=ft.padding.symmetric(16, 20),
    )
    password = ft.TextField(
        label="Contraseña", password=True, can_reveal_password=True, width=520,
        bgcolor=LIGHT_LILAC, border_radius=14, border=ft.InputBorder.NONE,
        content_padding=ft.padding.symmetric(16, 20),
    )

    def _submit(e=None):
        on_submit(email.value, password.value)

    login_cta = ft.ElevatedButton(
        "Log In", width=360, height=54,
        bgcolor=PRIMARY_GREEN, color=WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=27)),
        on_click=_submit,
    )

    forget_row = ft.Row(
        [ft.TextButton("Forget Password", style=ft.ButtonStyle(color=BACK_BLUE))],
        alignment=ft.MainAxisAlignment.END, width=520,
    )

    back_icon = ft.Image(
        src=os.path.join(assets_dir, "back.png"), width=28, height=28,
        error_content=ft.Text("<", color=BACK_BLUE, size=28, weight=ft.FontWeight.BOLD),
    )
    back_btn = ft.GestureDetector(on_tap=on_back, content=ft.Container(padding=8, content=back_icon))

    form = ft.Column(
        controls=[
            ft.Text("Log In", size=32, weight=ft.FontWeight.BOLD, color=PRIMARY_GREEN),
            ft.Container(height=20),
            ft.Container(
                width=560,
                content=ft.Column(
                    controls=[
                        ft.Text("Email", color=PRIMARY_GREEN), email,
                        ft.Container(height=10),
                        ft.Text("Contraseña", color=PRIMARY_GREEN), password,
                        ft.Container(height=6), forget_row,
                    ],
                    spacing=6, horizontal_alignment=ft.CrossAxisAlignment.START,
                ),
                alignment=ft.alignment.center,
            ),
            ft.Container(height=12), login_cta,
            ft.Container(height=6),
            ft.Row(
                controls=[
                    ft.Text("Don't have an account? "),
                    ft.TextButton("Sign Up", style=ft.ButtonStyle(color=BACK_BLUE)),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        spacing=12, alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return ft.Container(
        width=PANEL_W, height=PANEL_H,
        bgcolor=WHITE, border_radius=22, border=ft.border.all(1, BORDER_SOFT),
        content=ft.Stack(
            controls=[ft.Container(content=back_btn, left=16, top=12),
                      ft.Container(expand=True, content=form)]
        ),
    )

# ---------- VISTA: HOME ----------
def home_view(assets_dir: str, display_name: str, on_logout):
    logout_btn = ft.ElevatedButton(
        "Cerrar sesión", bgcolor=PRIMARY_GREEN, color=WHITE,
        on_click=on_logout, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=24)),
    )

    header = ft.Row(
        controls=[
            ft.Text(f"Hola, {display_name}", size=20, weight=ft.FontWeight.BOLD, color=PRIMARY_GREEN),
            ft.Container(expand=True),
            logout_btn,
        ],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    body = ft.Column(
        controls=[
            ft.Text("Contenido interno de ejemplo.", color=PRIMARY_GREEN),
            ft.Text("Aquí iría tu dashboard/pantalla privada.", color=PRIMARY_GREEN),
        ],
        spacing=8,
    )

    return ft.Container(
        width=PANEL_W, height=PANEL_H, bgcolor=WHITE,
        border_radius=22, border=ft.border.all(1, BORDER_SOFT),
        padding=20,
        content=ft.Column(controls=[header, ft.Divider(), body], expand=True),
    )
