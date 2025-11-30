# app/views/views.py
import os
import flet as ft

FULL_BLACK = "#000000"
LIGHT_GREY = "#D8D8D8"
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
        bgcolor=LIGHT_GREY, color=PRIMARY_GREEN,
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
def login_view(assets_dir: str, on_back, on_submit, on_go_signup, on_go_recover):
    FIELD_W = 460
    FONT_SIZE_LABEL = 14
    FIELD_SPACE = 10

    email = ft.TextField(
        label="Email", hint_text="example@example.com", width=FIELD_W,
        bgcolor=LIGHT_GREY, border_radius=12, border=ft.InputBorder.NONE,
        content_padding=ft.padding.symmetric(12, 14),
        color="#000000", hint_style=ft.TextStyle(color="#666666"),
    )
    password = ft.TextField(
        label="Contraseña", hint_text="Contraseña",
        password=True, can_reveal_password=True, width=FIELD_W,
        bgcolor=LIGHT_GREY, border_radius=12, border=ft.InputBorder.NONE,
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
        bgcolor=LIGHT_GREY, border_radius=12, border=ft.InputBorder.NONE,
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
        bgcolor=LIGHT_GREY, border_radius=12, border=ft.InputBorder.NONE,
        content_padding=ft.padding.symmetric(12, 14),
        color="#000000", hint_style=ft.TextStyle(color="#666666"),
    )
    confirm = ft.TextField(
        label="Confirmar Contraseña", hint_text="Confirmar Contraseña",
        password=True, can_reveal_password=True, width=FIELD_W,
        bgcolor=LIGHT_GREY, border_radius=12, border=ft.InputBorder.NONE,
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
        bgcolor=LIGHT_GREY, border_radius=12, border=ft.InputBorder.NONE,
        content_padding=ft.padding.symmetric(12, 14),
        color="#000000",                 # 👈 texto negro
        hint_style=ft.TextStyle(color="#666666"),  # 👈 texto del placeholder gris oscuro
    )
    password = ft.TextField(
        label="Contraseña", hint_text="Contraseña",
        password=True, can_reveal_password=True, width=FIELD_W,
        bgcolor=LIGHT_GREY, border_radius=12, border=ft.InputBorder.NONE,
        content_padding=ft.padding.symmetric(12, 14),
        color="#000000",
        hint_style=ft.TextStyle(color="#666666"),
    )
    email = ft.TextField(
        label="Email", hint_text="example@example.com", width=FIELD_W,
        bgcolor=LIGHT_GREY, border_radius=12, border=ft.InputBorder.NONE,
        content_padding=ft.padding.symmetric(12, 14),
        color="#000000",
        hint_style=ft.TextStyle(color="#666666"),
    )
    dob = ft.TextField(
        label="Fecha De Nacimiento", hint_text="DD / MM / YYYY", width=FIELD_W,
        bgcolor=LIGHT_GREY, border_radius=12, border=ft.InputBorder.NONE,
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
def home_view(assets_dir: str, display_name: str, on_logout, on_dashboard):
    logout_btn = ft.ElevatedButton(
        "Cerrar sesión", bgcolor=PRIMARY_GREEN, color=WHITE,
        on_click=on_logout, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=24)),
    )

    # Nuevo botón para ir a Dashboard
    dashboard_btn = ft.ElevatedButton(
        "Ver Sensores y Actuadores", color=WHITE,
        on_click=on_dashboard, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=24)),
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
            ft.Container(height=20),
            dashboard_btn,  # ⬅️ botón para ir al dashboard
        ],
        spacing=8,
    )

    return ft.Container(
        width=PANEL_W, height=PANEL_H, bgcolor=WHITE,
        border_radius=22, border=ft.border.all(1, BORDER_SOFT),
        padding=20,
        content=ft.Column(controls=[header, ft.Divider(), body], expand=True),
    )

# ---------- VISTA: dashboard(actuadores/sensores HISTORIAL) ----------
def dashboard_view(assets_dir: str, display_name: str, on_home):
    PRIMARY_GREEN = "#2D4A46"
    WHITE = "#FFFFFF"
    LIGHT_GREEN = "#31B057"
    DARK_BG = "#2D4A46"
    BORDER_SOFT = "#00000014"

    # Datos simulados
    sensores_data = [
        {"nombre": "Sensor 1", "info": ["Temperatura: 22°C", "Humedad: 45%", "Estado: OK"]},
        {"nombre": "Sensor 2", "info": ["Temperatura: 25°C", "Humedad: 50%", "Estado: OK"]},
        {"nombre": "Sensor 3", "info": ["Temperatura: 20°C", "Humedad: 42%", "Estado: Alerta"]},
    ]
    actuadores_data = [
        {"nombre": "Actuador 1", "info": ["Tipo: Motor", "Potencia: 5W", "Estado: Activo"]},
        {"nombre": "Actuador 2", "info": ["Tipo: Luz LED", "Potencia: 2W", "Estado: Inactivo"]},
        {"nombre": "Actuador 3", "info": ["Tipo: Ventilador", "Potencia: 10W", "Estado: Activo"]},
    ]

    def generar_lista(items):
        rows = []
        for d in items:
            info_text = [ft.Text(f"- {i}", color="black") for i in d["info"]]
            rows.append(
                ft.Column(
                    controls=[
                        ft.Text(f"{d['nombre']} (Nombre)", size=16, weight=ft.FontWeight.BOLD, color="black"),
                        *info_text,
                        ft.Text("...", color="black"),
                        ft.Container(height=10)
                    ]
                )
            )
        return rows

    # Creamos referencias para contenido dinámico y pestañas
    content_area = ft.Ref[ft.Column]()
    btn_sensores = ft.Ref[ft.Container]()
    btn_actuadores = ft.Ref[ft.Container]()

    def build(page: ft.Page):
        # Contenido inicial
        content_area.current = ft.Column(controls=generar_lista(sensores_data), spacing=12)

        # ----------- Callbacks dentro de build para acceder a page -----------
        def mostrar_sensores(e=None):
            btn_sensores.current.bgcolor = LIGHT_GREEN
            btn_actuadores.current.bgcolor = WHITE
            btn_actuadores.current.content.controls[0].color = "black"
            btn_sensores.current.content.controls[0].color = WHITE
            content_area.current.controls = generar_lista(sensores_data)
            scrollable_content.content.controls = content_area.current.controls
            page.update()

        def mostrar_actuadores(e=None):
            btn_actuadores.current.bgcolor = LIGHT_GREEN
            btn_sensores.current.bgcolor = WHITE
            btn_sensores.current.content.controls[0].color = "black"
            btn_actuadores.current.content.controls[0].color = WHITE
            content_area.current.controls = generar_lista(actuadores_data)
            scrollable_content.content.controls = content_area.current.controls  # actualizar ListView
            page.update()

        # ----------- Botones de pestañas -----------
        btn_sensores.current = ft.Container(
            width=180, height=40, bgcolor=LIGHT_GREEN, border_radius=20,
            content=ft.Row([ft.Text("Sensores", size=16, weight=ft.FontWeight.BOLD, color=WHITE)],
                           alignment=ft.MainAxisAlignment.CENTER),
            on_click=mostrar_sensores
        )

        btn_actuadores.current = ft.Container(
            width=180, height=40, bgcolor=WHITE, border_radius=20,
            content=ft.Row([ft.Text("Actuadores", size=16, weight=ft.FontWeight.BOLD, color="black")],
                           alignment=ft.MainAxisAlignment.CENTER),
            on_click=mostrar_actuadores
        )

        # ----------- Cabecera -----------
        header = ft.Row(
            controls=[
                ft.Image(src=os.path.join(assets_dir, "user.png"), width=50, height=50, border_radius=25),
                ft.Column([ft.Text("Hi, WelcomeBack", size=14, color="black"),
                           ft.Text(display_name, size=16, weight=ft.FontWeight.BOLD, color="black")],
                          spacing=2),
                ft.Container(expand=True),
                ft.IconButton(icon=ft.Icons.SETTINGS, icon_color="black"),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        tabs = ft.Row(controls=[btn_sensores.current, btn_actuadores.current],
                      alignment=ft.MainAxisAlignment.CENTER, spacing=10)

        scrollable_content = ft.Container(
            expand=True, bgcolor=WHITE, border_radius=8,
            content=ft.ListView(content_area.current.controls, expand=True, spacing=12, padding=10)
        )

        home_btn = ft.IconButton(
            icon=ft.Icons.GRID_VIEW,
            icon_color=WHITE,
            icon_size=36,
            bgcolor=DARK_BG,
            on_click=on_home,  # 👈 este se ejecutará
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=16)),
        )

        bottom_bar = ft.Container(
            content=ft.Row([home_btn], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=DARK_BG, height=70,
            border_radius=ft.border_radius.only(bottom_left=22, bottom_right=22)
        )

        # ----------- Vista completa -----------
        page.bgcolor = DARK_BG
        page.padding = 0
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        return ft.Container(
            width=980, height=640, bgcolor=WHITE, border_radius=22,
            border=ft.border.all(1, BORDER_SOFT),
            content=ft.Column(
                controls=[ft.Container(padding=20, content=header),
                          tabs,
                          ft.Container(height=10),
                          ft.Container(expand=True, content=scrollable_content,
                                       padding=ft.padding.symmetric(horizontal=12)),
                          bottom_bar],
                expand=True, spacing=6
            ),
        )

    return build
