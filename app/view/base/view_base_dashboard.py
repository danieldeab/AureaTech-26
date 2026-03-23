import os
import flet as ft
from pathlib import Path
from app.view.theme import (
    PRIMARY_GREEN,
    WHITE,
    BACK_BLUE,
    BRAND_ACCENT_BLUE,
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
        on_back=None,
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
        self.on_back = on_back
    

    # --------------------------------------------------------
    # HEADER BAR
    # --------------------------------------------------------
    def _header(self):

        back_btn = None
        if self.on_back:
            back_btn = ft.GestureDetector(
                on_tap=lambda e: self.on_back(),
                content=ft.Image(
                    src=f"{self.page.assets_dir}/back.png",
                    width=26,
                    height=26,
                    error_content=ft.Text("<"),
                ),
            )

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
            color=BRAND_ACCENT_BLUE,
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
                        controls=[
                            back_btn if back_btn else ft.Container(width=0),
                            avatar,
                            info_column
                        ],
                    ),
                    right_icon,
                ],
            ),
        )

    # --------------------------------------------------------
    # BOTTOM NAVIGATION (role-based)
    # --------------------------------------------------------
    def _bottom_nav(self) -> ft.Control:
        role = self.role.lower()

        # Common buttons:
        logout_btn = ft.IconButton(
            icon=ft.icons.LOGOUT,
            icon_color=FULL_BLACK,
            on_click=lambda e: self.on_logout(),
        )

        alerts_btn = ft.IconButton(
            icon=ft.icons.CRISIS_ALERT,
            icon_color=FULL_BLACK,
            on_click=lambda e: self.on_alerts(),
        )

        dashboard_btn = ft.IconButton(
            icon=ft.icons.HOME,
            icon_color=FULL_BLACK,
            on_click=lambda e: self.on_dashboard(),
        )

        # Role-specific buttons
        info_btn = ft.IconButton(
            icon=ft.icons.INFO_OUTLINE,
            icon_color=FULL_BLACK,
            on_click=lambda e: self.controller.show_info_control(),
        )

        history_btn = ft.IconButton(
            icon=ft.icons.HISTORY,
            icon_color=FULL_BLACK,
            on_click=lambda e: self.controller.show_history(),
        )

        user_mgmt_btn = ft.IconButton(
            icon=ft.icons.GROUPS,
            icon_color=FULL_BLACK,
            on_click=lambda e: self.controller.show_user_management(),
        )

        # Build bar according to role
        if role == "neighbor":
            controls = [
                dashboard_btn,
                alerts_btn,
                logout_btn,
            ]

        elif role == "technician":
            controls = [
                dashboard_btn,
                info_btn,
                alerts_btn,
                history_btn,
                logout_btn,
            ]

        elif role == "admin":
            controls = [
                user_mgmt_btn,
                dashboard_btn,
                alerts_btn,
                info_btn,
                history_btn,
                logout_btn,
            ]

        else:
            controls = [dashboard_btn, logout_btn]

        return ft.Container(
            bgcolor=BG_CARD_PRIMARY,
            padding=12,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=controls,
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
