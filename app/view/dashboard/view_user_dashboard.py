# app/view/dashboard/view_user_dashboard.py

import flet as ft
from app.view.base.view_base_dashboard import BaseDashboardView
from app.view.theme import PRIMARY_GREEN, WHITE


class UserDashboardView(BaseDashboardView):
    """
    Dashboard view for a normal vecino/standard user.
    Displays simple sensor summary tiles.
    More detailed navigation is disabled for this role.
    """
    def __init__(self, page, controller, user, role, on_dashboard, on_settings, on_alerts, on_logout):
        super().__init__(
            page=page,
            controller=controller,
            user=user,
            role=role,
            on_settings=on_settings,
            on_dashboard=on_dashboard,
            on_alerts=on_alerts,
            on_logout=on_logout,
        )

    def build_body(self) -> ft.Control:
        tile_style = lambda title, value: ft.Container(
            padding=20,
            bgcolor=WHITE,
            border_radius=16,
            content=ft.Column(
                spacing=5,
                controls=[
                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=PRIMARY_GREEN),
                    ft.Text(value, size=14, color=PRIMARY_GREEN),
                ],
            ),
        )

        return ft.Column(
            spacing=20,
            controls=[
                tile_style("Temperature", "23°C"),
                tile_style("Humidity", "56%"),
                tile_style("Air Quality", "Good"),
                tile_style("Noise Level", "Moderate"),
                tile_style("Light Level", "Bright"),
                tile_style("CO2 Level", "Normal"),
                tile_style("Motion Detection", "No Motion"),
            ],
        )
