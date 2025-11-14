# app/views/views.py
import os
import flet as ft

FULL_BLACK = "#000000"
LIGHT_LILAC = "#E9EDFF"
PRIMARY_GREEN = "#2D4A46"
WHITE = "#FFFFFF"
BORDER_SOFT = "#00000014"
BACK_BLUE = "#3F66FF"
PANEL_W = 980
PANEL_H = 640

# ---------- VISTA: MENÚ PRINCIPAL ----------
def menu_view(assets_dir: str, on_login_click, on_signup_click):
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
        on_click=on_signup_click,
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
# ---------- VISTA: LOGIN ----------
def login_view(assets_dir: str, on_back, on_submit, on_go_signup, on_go_recover):
    FIELD_W = 460
    FONT_SIZE_LABEL = 14
    FIELD_SPACE = 10

    email = ft.TextField(
        label="Email", hint_text="example@example.com", width=FIELD_W,
        bgcolor=LIGHT_LILAC, border_radius=12, border=ft.InputBorder.NONE,
        content_padding=ft.padding.symmetric(12, 14),
        color="#000000", hint_style=ft.TextStyle(color="#666666"),
    )
    password = ft.TextField(
        label="Contraseña", hint_text="Contraseña",
        password=True, can_reveal_password=True, width=FIELD_W,
        bgcolor=LIGHT_LILAC, border_radius=12, border=ft.InputBorder.NONE,
        content_padding=ft.padding.symmetric(12, 14),
        color="#000000", hint_style=ft.TextStyle(color="#666666"),
    )

    def _submit(e=None): on_submit(email.value, password.value)

    login_cta = ft.ElevatedButton(
        "Log In", width=260, height=48,
        bgcolor=PRIMARY_GREEN, color=WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=24)),
        on_click=_submit,
    )

    # 👇 Link a recuperación
    forget_row = ft.Row(
        [ft.TextButton("Forget Password", style=ft.ButtonStyle(color=BACK_BLUE), on_click=on_go_recover)],
        alignment=ft.MainAxisAlignment.END, width=FIELD_W,
    )

    back_icon = ft.Image(
        src=os.path.join(assets_dir, "back.png"), width=26, height=26,
        error_content=ft.Text("<", color=BACK_BLUE, size=26, weight=ft.FontWeight.BOLD),
    )
    back_btn = ft.GestureDetector(on_tap=on_back, content=ft.Container(padding=6, content=back_icon))

    form = ft.Column(
        controls=[
            ft.Text("Log In", size=28, weight=ft.FontWeight.BOLD, color=PRIMARY_GREEN),
            ft.Container(height=24),
            ft.Text("Email", color=PRIMARY_GREEN, size=FONT_SIZE_LABEL), email,
            ft.Container(height=FIELD_SPACE),
            ft.Text("Contraseña", color=PRIMARY_GREEN, size=FONT_SIZE_LABEL), password,
            ft.Container(height=6), forget_row,
            ft.Container(height=14), login_cta,
            ft.Container(height=6),
            ft.Row(
                controls=[ft.Text("Don't have an account? "),
                          ft.TextButton("Sign Up", style=ft.ButtonStyle(color=BACK_BLUE), on_click=on_go_signup)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        spacing=6, alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return ft.Container(
        width=PANEL_W, height=PANEL_H, bgcolor=WHITE, border_radius=22,
        border=ft.border.all(1, BORDER_SOFT), padding=ft.padding.only(top=30, bottom=20),
        content=ft.Stack(controls=[
            ft.Container(content=back_btn, left=16, top=12),
            ft.Container(expand=True, alignment=ft.alignment.center, content=form),
        ]),
    )

# ---------- VISTA: RECUPERAR CUENTA (email) ----------
def recover_view(assets_dir: str, on_back, on_submit, on_go_login):
    FIELD_W = 460
    email = ft.TextField(
        label="Correo", hint_text="example@example.com", width=FIELD_W,
        bgcolor=LIGHT_LILAC, border_radius=12, border=ft.InputBorder.NONE,
        content_padding=ft.padding.symmetric(12, 14),
        color="#000000", hint_style=ft.TextStyle(color="#666666"),
    )

    def _submit(e=None): on_submit(email.value)

    send_btn = ft.ElevatedButton(
        "Enviar enlace", width=260, height=48,
        bgcolor=PRIMARY_GREEN, color=WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=24)),
        on_click=_submit,
    )

    back_icon = ft.Image(
        src=os.path.join(assets_dir, "back.png"), width=26, height=26,
        error_content=ft.Text("<", color=BACK_BLUE, size=26, weight=ft.FontWeight.BOLD),
    )
    back_btn = ft.GestureDetector(on_tap=on_back, content=ft.Container(padding=6, content=back_icon))

    form = ft.Column(
        controls=[
            ft.Text("Recuperar cuenta", size=28, weight=ft.FontWeight.BOLD, color=PRIMARY_GREEN),
            ft.Container(height=20),
            ft.Text("Ingresá tu correo para enviar el enlace (simulado).", color=PRIMARY_GREEN, size=14),
            ft.Container(height=18),
            email,
            ft.Container(height=14),
            send_btn,
            ft.Container(height=10),
            ft.Row([ft.Text("¿Recordaste tu contraseña? "),
                    ft.TextButton("Log in", style=ft.ButtonStyle(color=BACK_BLUE), on_click=on_go_login)],
                   alignment=ft.MainAxisAlignment.CENTER),
        ],
        spacing=6, alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return ft.Container(
        width=PANEL_W, height=PANEL_H, bgcolor=WHITE, border_radius=22, border=ft.border.all(1, BORDER_SOFT),
        padding=ft.padding.only(top=30, bottom=20),
        content=ft.Stack(controls=[
            ft.Container(content=back_btn, left=16, top=12),
            ft.Container(expand=True, alignment=ft.alignment.center, content=form),
        ]),
    )

# ---------- VISTA: SET PASSWORD (2 campos) ----------
def reset_password_view(assets_dir: str, email: str, on_back, on_submit):
    FIELD_W = 460
    FONT_SIZE_LABEL = 14

    pwd = ft.TextField(
        label="Contraseña", hint_text="Contraseña",
        password=True, can_reveal_password=True, width=FIELD_W,
        bgcolor=LIGHT_LILAC, border_radius=12, border=ft.InputBorder.NONE,
        content_padding=ft.padding.symmetric(12, 14),
        color="#000000", hint_style=ft.TextStyle(color="#666666"),
    )
    confirm = ft.TextField(
        label="Confirmar Contraseña", hint_text="Confirmar Contraseña",
        password=True, can_reveal_password=True, width=FIELD_W,
        bgcolor=LIGHT_LILAC, border_radius=12, border=ft.InputBorder.NONE,
        content_padding=ft.padding.symmetric(12, 14),
        color="#000000", hint_style=ft.TextStyle(color="#666666"),
    )

    def _submit(e=None): on_submit(email, pwd.value, confirm.value)

    create_btn = ft.ElevatedButton(
        "Crear Nueva Contraseña", width=280, height=48,
        bgcolor=PRIMARY_GREEN, color=WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=24)),
        on_click=_submit,
    )

    back_icon = ft.Image(
        src=os.path.join(assets_dir, "back.png"), width=26, height=26,
        error_content=ft.Text("<", color=BACK_BLUE, size=26, weight=ft.FontWeight.BOLD),
    )
    back_btn = ft.GestureDetector(on_tap=on_back, content=ft.Container(padding=6, content=back_icon))

    form = ft.Column(
        controls=[
            ft.Text("Set Password", size=28, weight=ft.FontWeight.BOLD, color=PRIMARY_GREEN),
            ft.Container(height=26),
            ft.Text("Contraseña", color=PRIMARY_GREEN, size=FONT_SIZE_LABEL), pwd,
            ft.Container(height=12),
            ft.Text("Confirmar Contraseña", color=PRIMARY_GREEN, size=FONT_SIZE_LABEL), confirm,
            ft.Container(height=18),
            create_btn,
        ],
        spacing=6, alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return ft.Container(
        width=PANEL_W, height=PANEL_H, bgcolor=WHITE, border_radius=22, border=ft.border.all(1, BORDER_SOFT),
        padding=ft.padding.only(top=30, bottom=20),
        content=ft.Stack(controls=[
            ft.Container(content=back_btn, left=16, top=12),
            ft.Container(expand=True, alignment=ft.alignment.center, content=form),
        ]),
    )

# ---------- VISTA: SIGN UP ----------
def sign_up_view(assets_dir: str, on_back, on_submit, on_go_login):
    FIELD_W = 460
    FONT_SIZE_LABEL = 14
    FIELD_SPACE = 8

    fullname = ft.TextField(
        label="Nombre completo", hint_text="Nombre completo", width=FIELD_W,
        bgcolor=LIGHT_LILAC, border_radius=12, border=ft.InputBorder.NONE,
        content_padding=ft.padding.symmetric(12, 14),
        color="#000000",                 # 👈 texto negro
        hint_style=ft.TextStyle(color="#666666"),  # 👈 texto del placeholder gris oscuro
    )
    password = ft.TextField(
        label="Contraseña", hint_text="Contraseña",
        password=True, can_reveal_password=True, width=FIELD_W,
        bgcolor=LIGHT_LILAC, border_radius=12, border=ft.InputBorder.NONE,
        content_padding=ft.padding.symmetric(12, 14),
        color="#000000",
        hint_style=ft.TextStyle(color="#666666"),
    )
    email = ft.TextField(
        label="Email", hint_text="example@example.com", width=FIELD_W,
        bgcolor=LIGHT_LILAC, border_radius=12, border=ft.InputBorder.NONE,
        content_padding=ft.padding.symmetric(12, 14),
        color="#000000",
        hint_style=ft.TextStyle(color="#666666"),
    )
    dob = ft.TextField(
        label="Fecha De Nacimiento", hint_text="DD / MM / YYYY", width=FIELD_W,
        bgcolor=LIGHT_LILAC, border_radius=12, border=ft.InputBorder.NONE,
        content_padding=ft.padding.symmetric(12, 14),
        color="#000000",
        hint_style=ft.TextStyle(color="#666666"),
    )

    def _submit(e=None):
        on_submit(fullname.value, email.value, password.value, dob.value)

    signup_cta = ft.ElevatedButton(
        "Sign Up", width=260, height=48,
        bgcolor=PRIMARY_GREEN, color=WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=24)),
        on_click=_submit,
    )

    terms = ft.Text(
        "By continuing, you agree to Terms of Use and Privacy Policy.",
        size=11, color=BACK_BLUE, text_align=ft.TextAlign.CENTER,
    )

    back_icon = ft.Image(
        src=os.path.join(assets_dir, "back.png"), width=26, height=26,
        error_content=ft.Text("<", color=BACK_BLUE, size=26, weight=ft.FontWeight.BOLD),
    )
    back_btn = ft.GestureDetector(on_tap=on_back, content=ft.Container(padding=6, content=back_icon))

    form = ft.Column(
        controls=[
            ft.Text("New Account", size=28, weight=ft.FontWeight.BOLD, color=PRIMARY_GREEN),
            ft.Container(height=16),
            ft.Text("Nombre completo", color=PRIMARY_GREEN, size=FONT_SIZE_LABEL), fullname,
            ft.Container(height=FIELD_SPACE),
            ft.Text("Contraseña", color=PRIMARY_GREEN, size=FONT_SIZE_LABEL), password,
            ft.Container(height=FIELD_SPACE),
            ft.Text("Email", color=PRIMARY_GREEN, size=FONT_SIZE_LABEL), email,
            ft.Container(height=FIELD_SPACE),
            ft.Text("Fecha De Nacimiento", color=PRIMARY_GREEN, size=FONT_SIZE_LABEL), dob,
            ft.Container(height=14),
            terms,
            ft.Container(height=10),
            signup_cta,
            ft.Container(height=6),
            ft.Row(
                controls=[
                    ft.Text("already have an account? "),
                    ft.TextButton("Log in", style=ft.ButtonStyle(color=BACK_BLUE), on_click=on_go_login),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        spacing=4,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return ft.Container(
        width=PANEL_W,
        height=PANEL_H,
        bgcolor=WHITE,
        border_radius=22,
        border=ft.border.all(1, BORDER_SOFT),
        padding=ft.padding.only(top=30, bottom=20),
        content=ft.Stack(
            controls=[
                ft.Container(content=back_btn, left=16, top=12),
                ft.Container(
                    expand=True,
                    alignment=ft.alignment.center,
                    content=form,
                ),
            ]
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

