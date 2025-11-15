# app/views/ViewGestionUsuario.py
import flet as ft

# --- mismas constantes que en tu views.py (importalas si ya existen) ---
FULL_BLACK = "#000000"
LIGHT_LILAC = "#E9EDFF"
PRIMARY_GREEN = "#2D4A46"
WHITE = "#FFFFFF"
BORDER_SOFT = "#00000014"
BACK_BLUE = "#3F66FF"
PANEL_W = 980
PANEL_H = 640
# ----------------------------------------------------------------------

class UserItemVM:
    def __init__(self, id: str, display_name: str, info_lines: list[str], can_delete: bool = True):
        self.id = id
        self.display_name = display_name
        self.info_lines = info_lines or []
        self.can_delete = can_delete


def user_management_view(
    assets_dir: str,
    items: list[UserItemVM],
    on_back, on_dashboard, on_edit, on_delete
) -> ft.Control:
    """Vista de Gestión de Usuarios (compatible con Flet sin ft.icons)."""

    # ---------- HEADER ----------
    top_stripe = ft.Container(height=6, bgcolor=BACK_BLUE)
    avatar = ft.CircleAvatar(
        radius=18, bgcolor="#CCD6DD",
        content=ft.Text("JD", size=12, weight=ft.FontWeight.BOLD, color=FULL_BLACK),
    )
    welcome = ft.Column(
        spacing=0,
        controls=[
            ft.Text("Hi, WelcomeBack", size=12, color="#4F4F4F"),
            ft.Text("John Doe", size=14, weight=ft.FontWeight.BOLD, color=FULL_BLACK),
        ],
    )
    settings_btn = ft.IconButton(
        icon="settings",  # <-- string en vez de ft.icons.SETTINGS
        icon_color=FULL_BLACK,
        style=ft.ButtonStyle(
            bgcolor={ft.ControlState.DEFAULT: "#EEEEEE"},
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
        on_click=lambda e: on_dashboard(),
    )
    header_bar = ft.Container(
        padding=ft.padding.symmetric(12, 16),
        bgcolor=WHITE,
        content=ft.Row(
            controls=[avatar, welcome, ft.Container(expand=True), settings_btn],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )
    header = ft.Column(spacing=0, controls=[top_stripe, header_bar])

    # ---------- ITEM CARD ----------
    def build_user_card(vm: UserItemVM) -> ft.Control:
        title = ft.Text(vm.display_name, size=18, weight=ft.FontWeight.BOLD, color=FULL_BLACK)
        info_labels = [ft.Text(line, size=14, color=FULL_BLACK) for line in vm.info_lines]
        left_col = ft.Column(spacing=6, controls=[title, *info_labels])

        btn_edit = ft.IconButton(
            icon="settings",  # <-- string
            tooltip="Editar",
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: "#EEEEEE"},
                color={ft.ControlState.DEFAULT: FULL_BLACK},
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            on_click=lambda e, _vm=vm: on_edit(_vm),
        )
        btn_delete = ft.IconButton(
            icon="delete_outline",  # <-- string
            tooltip="Eliminar",
            disabled=not vm.can_delete,
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: "#FFE5E5"},
                color={ft.ControlState.DEFAULT: "#C0392B"},
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            on_click=lambda e, _vm=vm: on_delete(_vm),
        )
        actions = ft.Column(spacing=10, horizontal_alignment=ft.CrossAxisAlignment.END,
                            controls=[btn_edit, btn_delete])

        card = ft.Container(
            bgcolor=LIGHT_LILAC,
            border=ft.border.all(1, WHITE),
            border_radius=12,
            padding=10,
            content=ft.Row([ft.Expanded(left_col), actions], vertical_alignment=ft.CrossAxisAlignment.START),
        )
        return ft.Container(padding=ft.padding.symmetric(6, 8), content=card)

    # ---------- LISTA ----------
    list_view = ft.ListView(expand=True, spacing=14, auto_scroll=False, padding=16)
    list_view.controls = [build_user_card(vm) for vm in (items or [])]

    # ---------- FOOTER ----------
    btn_back = ft.IconButton(
        icon="undo_rounded",  # <-- string
        icon_size=28,
        style=ft.ButtonStyle(
            bgcolor={ft.ControlState.DEFAULT: PRIMARY_GREEN},
            color={ft.ControlState.DEFAULT: WHITE},
            shape=ft.RoundedRectangleBorder(radius=22),
        ),
        on_click=lambda e: on_back(),
    )
    btn_dash = ft.TextButton(
        content=ft.Row([ft.Icon(name="dashboard_outlined"), ft.Text("Tablero")], tight=True),
        # ft.Icon(name="...") también funciona con strings en versiones viejas
        style=ft.ButtonStyle(
            bgcolor={ft.ControlState.DEFAULT: PRIMARY_GREEN},
            color={ft.ControlState.DEFAULT: WHITE},
            padding=ft.padding.all(14),
            shape=ft.RoundedRectangleBorder(radius=22),
        ),
        on_click=lambda e: on_dashboard(),
    )
    footer_pill = ft.Container(
        bgcolor="#2F4F4F", height=72, border_radius=14,
        content=ft.Row(
            [btn_back, ft.Container(expand=True), btn_dash],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True, padding=ft.padding.symmetric(10, 16),
        ),
    )
    footer = ft.Container(padding=ft.padding.only(10, 10, 14, 14), content=footer_pill)

    # ---------- PANEL ----------
    return ft.Container(
        width=PANEL_W, height=PANEL_H,
        bgcolor=WHITE, border_radius=22,
        border=ft.border.all(1, BORDER_SOFT),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Column(
            spacing=0,
            controls=[
                header,
                ft.Container(expand=True, bgcolor=PRIMARY_GREEN, content=list_view),
                footer,
            ],
        ),
    )


# ---------- DEMO para probar rápido ----------
def _demo_main(page: ft.Page):
    page.title = "Gestión de Usuarios — Demo"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = "stretch"
    page.vertical_alignment = "stretch"

    def snack(msg): page.open(ft.SnackBar(ft.Text(msg)))

    demo_items = [
        UserItemVM("u1", "Usuario 1 (Nombre)", ["-Info", "-Info", "-Info"], True),
        UserItemVM("u2", "Usuario 2 (Nombre)", ["-Info", "-Info", "-Info"], True),
        UserItemVM("u3", "Usuario 3 (Nombre)", ["-Info", "-Info"], False),
    ]

    view = user_management_view(
        assets_dir="",
        items=demo_items,
        on_back=lambda: snack("Volver"),
        on_dashboard=lambda: snack("Ir al tablero"),
        on_edit=lambda vm: snack(f"Editar: {vm.display_name}"),
        on_delete=lambda vm: snack(f"Eliminar: {vm.display_name}"),
    )

    page.add(ft.Container(width=PANEL_W, height=PANEL_H, alignment=ft.alignment.center, content=view))

if __name__ == "__main__":
   import flet as ft

# Paleta y medidas (ajusta si ya las importás)
FULL_BLACK = "#000000"
LIGHT_LILAC = "#E9EDFF"
PRIMARY_GREEN = "#2D4A46"
WHITE = "#FFFFFF"
BORDER_SOFT = "#00000014"
BACK_BLUE = "#3F66FF"
PANEL_W = 980
PANEL_H = 640

class UserItemVM:
    def __init__(self, id: str, display_name: str, info_lines: list[str], can_delete: bool = True):
        self.id = id
        self.display_name = display_name
        self.info_lines = info_lines or []
        self.can_delete = can_delete

def user_management_view(
    assets_dir: str,
    items: list[UserItemVM],
    on_back, on_dashboard, on_edit, on_delete
) -> ft.Control:
    # HEADER (sin ft.icons)
    top_stripe = ft.Container(height=6, bgcolor=BACK_BLUE)
    avatar = ft.CircleAvatar(radius=18, bgcolor="#CCD6DD",
                             content=ft.Text("JD", size=12, weight=ft.FontWeight.BOLD, color=FULL_BLACK))
    welcome = ft.Column(spacing=0, controls=[
        ft.Text("Hi, WelcomeBack", size=12, color="#4F4F4F"),
        ft.Text("John Doe", size=14, weight=ft.FontWeight.BOLD, color=FULL_BLACK),
    ])
    settings_btn = ft.TextButton("⚙", on_click=lambda e: on_dashboard(),
                                 style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8),
                                                      bgcolor={ft.ControlState.DEFAULT: "#EEEEEE"},
                                                      color={ft.ControlState.DEFAULT: FULL_BLACK},
                                                      padding=ft.padding.symmetric(6, 10)))
    header_bar = ft.Container(
        padding=ft.padding.symmetric(12, 16),
        bgcolor=WHITE,
        content=ft.Row([avatar, welcome, ft.Container(expand=True), settings_btn],
                       vertical_alignment=ft.CrossAxisAlignment.CENTER),
    )
    header = ft.Column(spacing=0, controls=[top_stripe, header_bar])

    # ITEM CARD (sin ft.icons)
    def build_user_card(vm: UserItemVM) -> ft.Control:
        title = ft.Text(vm.display_name, size=18, weight=ft.FontWeight.BOLD, color=FULL_BLACK)
        info_labels = [ft.Text(line, size=14, color=FULL_BLACK) for line in vm.info_lines]
        left_col = ft.Column(spacing=6, controls=[title, *info_labels])

        btn_edit = ft.TextButton("⚙ Editar",
                                 style=ft.ButtonStyle(
                                     bgcolor={ft.ControlState.DEFAULT: "#EEEEEE"},
                                     color={ft.ControlState.DEFAULT: FULL_BLACK},
                                     padding=ft.padding.symmetric(8, 10),
                                     shape=ft.RoundedRectangleBorder(radius=8),
                                 ),
                                 on_click=lambda e, _vm=vm: on_edit(_vm))
        btn_delete = ft.TextButton("🗑 Eliminar",
                                   disabled=not vm.can_delete,
                                   style=ft.ButtonStyle(
                                       bgcolor={ft.ControlState.DEFAULT: "#FFE5E5"},
                                       color={ft.ControlState.DEFAULT: "#C0392B"},
                                       padding=ft.padding.symmetric(8, 10),
                                       shape=ft.RoundedRectangleBorder(radius=8),
                                   ),
                                   on_click=lambda e, _vm=vm: on_delete(_vm))
        actions = ft.Column(spacing=10, horizontal_alignment=ft.CrossAxisAlignment.END,
                            controls=[btn_edit, btn_delete])

        card = ft.Container(
            bgcolor=LIGHT_LILAC,
            border=ft.border.all(1, WHITE),
            border_radius=12,
            padding=10,
            content=ft.Row([ft.Expanded(left_col), actions],
                           vertical_alignment=ft.CrossAxisAlignment.START),
        )
        return ft.Container(padding=ft.padding.symmetric(6, 8), content=card)

    list_view = ft.ListView(expand=True, spacing=14, auto_scroll=False, padding=16)
    list_view.controls = [build_user_card(vm) for vm in (items or [])]

    # FOOTER (sin ft.icons)
    btn_back = ft.TextButton("↩ Volver",
                             style=ft.ButtonStyle(
                                 bgcolor={ft.ControlState.DEFAULT: PRIMARY_GREEN},
                                 color={ft.ControlState.DEFAULT: WHITE},
                                 padding=ft.padding.symmetric(10, 16),
                                 shape=ft.RoundedRectangleBorder(radius=22),
                             ),
                             on_click=lambda e: on_back())
    btn_dash = ft.TextButton("⌇ Tablero",
                             style=ft.ButtonStyle(
                                 bgcolor={ft.ControlState.DEFAULT: PRIMARY_GREEN},
                                 color={ft.ControlState.DEFAULT: WHITE},
                                 padding=ft.padding.symmetric(10, 16),
                                 shape=ft.RoundedRectangleBorder(radius=22),
                             ),
                             on_click=lambda e: on_dashboard())
    footer_pill = ft.Container(
        bgcolor="#2F4F4F", height=72, border_radius=14,
        content=ft.Row([btn_back, ft.Container(expand=True), btn_dash],
                       alignment=ft.MainAxisAlignment.CENTER,
                       vertical_alignment=ft.CrossAxisAlignment.CENTER,
                       expand=True, padding=ft.padding.symmetric(10, 16)),
    )
    footer = ft.Container(padding=ft.padding.only(10, 10, 14, 14), content=footer_pill)

    return ft.Container(
        width=PANEL_W, height=PANEL_H, bgcolor=WHITE, border_radius=22, border=ft.border.all(1, BORDER_SOFT),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Column(spacing=0, controls=[header,
                                               ft.Container(expand=True, bgcolor=PRIMARY_GREEN, content=list_view),
                                               footer]),
    )

# DEMO
def _demo_main(page: ft.Page):
    page.title = "Gestión de Usuarios — Demo"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = "stretch"
    page.vertical_alignment = "stretch"

    def snack(msg): page.open(ft.SnackBar(ft.Text(msg)))

    view = user_management_view(
        assets_dir="",
        items=[
            UserItemVM("u1", "Usuario 1 (Nombre)", ["-Info", "-Info", "-Info"], True),
            UserItemVM("u2", "Usuario 2 (Nombre)", ["-Info", "-Info", "-Info"], True),
            UserItemVM("u3", "Usuario 3 (Nombre)", ["-Info", "-Info"], False),
        ],
        on_back=lambda: snack("Volver"),
        on_dashboard=lambda: snack("Ir al tablero"),
        on_edit=lambda vm: snack(f"Editar: {vm.display_name}"),
        on_delete=lambda vm: snack(f"Eliminar: {vm.display_name}"),
    )
    page.add(ft.Container(width=PANEL_W, height=PANEL_H, alignment=ft.alignment.center, content=view))

if __name__ == "__main__":
    ft.app(target=_demo_main)
