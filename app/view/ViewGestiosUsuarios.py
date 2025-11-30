# -*- coding: utf-8 -*-
# Compatible con Flet 0.28.3 (Py 3.13). Sin ft.icons, sin Row.padding, sin ft.Expanded.
import flet as ft

# Paleta / medidas
FULL_BLACK = "#000000"
LIGHT_GREY = "#D8D8D8"
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


class ViewGestionUsuario:
    def __init__(
        self,
        items: list[UserItemVM] | None = None,
        on_back=lambda: None,
        on_dashboard=lambda: None,
        on_edit=lambda vm: None,
        on_delete=lambda vm: None,
    ):
        self.items = items or []
        self.on_back = on_back
        self.on_dashboard = on_dashboard
        self.on_edit = on_edit
        self.on_delete = on_delete

        self._list = ft.ListView(expand=True, spacing=14, auto_scroll=False, padding=16)

        self.control = ft.Container(
            width=PANEL_W,
            height=PANEL_H,
            bgcolor=WHITE,
            border_radius=22,
            border=ft.border.all(1, BORDER_SOFT),
            content=ft.Column(
                spacing=0,
                controls=[
                    self._build_header(),
                    ft.Container(expand=True, bgcolor=PRIMARY_GREEN, content=self._list),
                    self._build_footer(),
                ],
            ),
        )

        self._render_list()

    # ------------ UI parts ------------
    def _build_header(self) -> ft.Control:
        stripe = ft.Container(height=6, bgcolor=BACK_BLUE)

        avatar = ft.CircleAvatar(
            radius=18,
            bgcolor="#CCD6DD",
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
            icon="settings",             # strings, no ft.icons
            icon_color=FULL_BLACK,
            on_click=lambda e: self.on_dashboard(),
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: "#EEEEEE"},
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

        bar = ft.Container(
            padding=ft.padding.symmetric(12, 16),
            bgcolor=WHITE,
            content=ft.Row(
                controls=[avatar, welcome, ft.Container(expand=True), settings_btn],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        return ft.Column(spacing=0, controls=[stripe, bar])

    def _build_footer(self) -> ft.Control:
        btn_back = ft.TextButton(
            "↩ Volver",
            on_click=lambda e: self.on_back(),
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: PRIMARY_GREEN},
                color={ft.ControlState.DEFAULT: WHITE},
                shape=ft.RoundedRectangleBorder(radius=22),
                padding=ft.padding.symmetric(10, 16),
            ),
        )
        btn_dash = ft.TextButton(
            "⌇ Tablero",
            on_click=lambda e: self.on_dashboard(),
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: PRIMARY_GREEN},
                color={ft.ControlState.DEFAULT: WHITE},
                shape=ft.RoundedRectangleBorder(radius=22),
                padding=ft.padding.symmetric(10, 16),
            ),
        )

        # Nada de Row.padding: el padding va en Container
        return ft.Container(
            padding=ft.padding.only(10, 10, 14, 14),
            content=ft.Container(
                bgcolor="#2F4F4F",
                height=72,
                border_radius=14,
                content=ft.Container(
                    padding=ft.padding.symmetric(10, 16),
                    content=ft.Row(
                        controls=[btn_back, ft.Container(expand=True), btn_dash],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ),
            ),
        )

    def _render_list(self):
        self._list.controls.clear()
        for vm in self.items:
            self._list.controls.append(self._build_user_card(vm))

    def _build_user_card(self, vm: UserItemVM) -> ft.Control:
        title = ft.Text(vm.display_name, size=18, weight=ft.FontWeight.BOLD, color=FULL_BLACK)
        info_labels = [ft.Text(line, size=14, color=FULL_BLACK) for line in vm.info_lines]
        left_col = ft.Column(spacing=6, controls=[title, *info_labels])

        btn_edit = ft.TextButton(
            "⚙ Editar",
            on_click=lambda e, _vm=vm: self.on_edit(_vm),
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: "#EEEEEE"},
                color={ft.ControlState.DEFAULT: FULL_BLACK},
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(8, 10),
            ),
        )
        btn_delete = ft.TextButton(
            "🗑 Eliminar",
            disabled=not vm.can_delete,
            on_click=lambda e, _vm=vm: self.on_delete(_vm),
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: "#FFE5E5"},
                color={ft.ControlState.DEFAULT: "#C0392B"},
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(8, 10),
            ),
        )

        actions = ft.Column(
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.END,
            controls=[btn_edit, btn_delete],
        )

        # >>> Cambio clave: reemplaza ft.Expanded(...) por Container(expand=True, content=...)
        row = ft.Row(
            controls=[ft.Container(expand=True, content=left_col), actions],
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        card = ft.Container(
            bgcolor=LIGHT_GREY,
            border=ft.border.all(1, WHITE),
            border_radius=12,
            padding=10,
            content=row,
        )
        return ft.Container(padding=ft.padding.symmetric(6, 8), content=card)


# ---------------- DEMO ejecutable ----------------
def main(page: ft.Page):
    page.title = "Gestión de Usuarios — Flet 0.28.3"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = "stretch"
    page.vertical_alignment = "stretch"

    def toast(msg: str):
        page.snack_bar = ft.SnackBar(ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    demo_items = [
        UserItemVM("u1", "Usuario 1 (Nombre)", ["-Info", "-Info", "-Info"], True),
        UserItemVM("u2", "Usuario 2 (Nombre)", ["-Info", "-Info", "-Info"], True),
        UserItemVM("u2", "Usuario 3 (Nombre)", ["-Info", "-Info", "-Info"], True),
        UserItemVM("u2", "Usuario 4 (Nombre)", ["-Info", "-Info", "-Info"], True),
        UserItemVM("u2", "Usuario 5 (Nombre)", ["-Info", "-Info", "-Info"], True),
        UserItemVM("u2", "Usuario 6 (Nombre)", ["-Info", "-Info", "-Info"], True),
        UserItemVM("u2", "Usuario 7 (Nombre)", ["-Info", "-Info", "-Info"], True),
        UserItemVM("u3", "Usuario 8 (Nombre)", ["-Info", "-Info"], False),
    ]

    vista = ViewGestionUsuario(
        items=demo_items,
        on_back=lambda: toast("Volver"),
        on_dashboard=lambda: toast("Ir al tablero"),
        on_edit=lambda vm: toast(f"Editar: {vm.display_name}"),
        on_delete=lambda vm: toast(f"Eliminar: {vm.display_name}"),
    )

    page.add(vista.control)


if __name__ == "__main__":
    ft.app(target=main)
