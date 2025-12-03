import os
import flet as ft
from pathlib import Path
from app.view.theme import (
    PRIMARY_GREEN,
    WHITE,
    BACK_BLUE,
    LIGHT_GREY,
    FULL_BLACK,
    PANEL_W,
    PANEL_H,
    BG_CARD_PRIMARY,
    BORDER_SOFT,
)


class BaseDashboardView(ft.UserControl):
    """
    Base class for all dashboards (vecino, admin, tecnico).
    Provides:
      - unified header (avatar + name + role)
      - unified bottom navigation bar
      - scrollable main content container
    """

    def __init__(
        self,
        page: ft.Page,
        controller,
        user,
        role: str,
        on_settings,
        on_dashboard,
        on_alerts,
        on_logout,
    ):
        super().__init__()
        self.page = page
        self.controller = controller
        self.user = user
        self.role = role

        # callbacks
        self.on_settings = on_settings
        self.on_dashboard = on_dashboard
        self.on_alerts = on_alerts
        self.on_logout = on_logout
    

    # --------------------------------------------------------
    # HEADER BAR
    # --------------------------------------------------------
    def _header(self):
        avatar_path = None
        if self.user and self.user.picture_url:
            avatar_path = self.user.picture_url
            avatar = ft.CircleAvatar(
                foreground_image_src=avatar_path,
                radius=24,
            )
        else:
            name = self.user.name if self.user else "User"
            initials = "".join([p[0].upper() for p in name.split()[:2]])

            avatar = ft.CircleAvatar(
                radius=24,
                bgcolor=PRIMARY_GREEN,
                content=ft.Text(
                    initials,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=WHITE,
                ),
            )

        name_text = ft.Text(
            self.user.name if self.user else "User",
            size=18,
            weight=ft.FontWeight.BOLD,
            color=FULL_BLACK,
        )

        role_text = ft.Text(
            self.role.capitalize(),
            size=14,
            color=LIGHT_GREY,
        )

        info_column = ft.Column(
            spacing=2,
            controls=[name_text, role_text],
        )

        right_icon = ft.IconButton(
            icon=ft.icons.SETTINGS,
            icon_color=BACK_BLUE,
            on_click=lambda e: self.on_settings(),
        )

        return ft.Container(
            bgcolor=WHITE,
            padding=15,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[avatar, info_column],
                    ),
                    right_icon,
                ],
            ),
        )

    # --------------------------------------------------------
    # BOTTOM NAVIGATION
    # --------------------------------------------------------
    def _bottom_nav(self):
        return ft.Container(
            bgcolor=WHITE,
            padding=ft.padding.symmetric(vertical=10, horizontal=20),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    # DASHBOARD
                    ft.GestureDetector(
                        on_tap=lambda e: self.on_dashboard(),
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=4,
                            controls=[
                                ft.Icon(ft.icons.DASHBOARD, color=PRIMARY_GREEN, size=22),
                                ft.Text("Dashboard", size=12, color=FULL_BLACK),
                            ],
                        ),
                    ),
                    # ALERTAS
                    ft.GestureDetector(
                        on_tap=lambda e: self.on_alerts(),
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=4,
                            controls=[
                                ft.Icon(ft.icons.WARNING, color=PRIMARY_GREEN, size=22),
                                ft.Text("Alertas", size=12, color=FULL_BLACK),
                            ],
                        ),
                    ),
                    # LOGOUT
                    ft.GestureDetector(
                        on_tap=lambda e: self.on_logout(),
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=4,
                            controls=[
                                ft.Icon(ft.icons.LOGOUT, color=PRIMARY_GREEN, size=22),
                                ft.Text("Salir", size=12, color=FULL_BLACK),
                            ],
                        ),
                    ),
                ],
            ),
        )

    # --------------------------------------------------------
    # MAIN LAYOUT (WORKING MODEL)
    # --------------------------------------------------------
    def build(self):
        return ft.Container(
            width=PANEL_W,
            height=PANEL_H,
            bgcolor=BG_CARD_PRIMARY or WHITE,
            border_radius=22,                           # <<<< MATCH AUTH RADIUS
            border=ft.border.all(1, BORDER_SOFT),       # <<<< MATCH AUTH BORDER
            padding=0,                                   # no inner padding here
            content=ft.Column(
                expand=True,
                spacing=0,
                controls=[
                    self._header(),
                    ft.Container(
                        expand=True,
                        alignment=ft.alignment.top_center,
                        content=ft.Container(
                            padding=ft.padding.only(
                                top=20, bottom=24, left=32, right=32
                            ),
                            bgcolor=WHITE,
                            border_radius=22,
                            content=ft.Column(
                                scroll=ft.ScrollMode.AUTO,
                                controls=[self.build_body()],
                            ),
                        ),
                    ),
                    self._bottom_nav(),
                ],
            ),
        )
