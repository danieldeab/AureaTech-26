# app/view/dashboard/view_tecnico_dashboard.py

import flet as ft
from app.view.base.view_base_dashboard import BaseDashboardView
from app.view.theme import PRIMARY_GREEN, WHITE


class TechnicianDashboardView(BaseDashboardView):
    """
    Dashboard for TECHNICIAN users.

    Focused more on sensors + alerts of their community.
    `summary` is the dict from DashboardService.get_dashboard_summary(...).to_dict().
    """

    def __init__(
        self,
        page,
        controller,
        user,
        role,
        community_id,
        summary: dict | None,
        on_dashboard,
        on_settings,
        on_alerts,
        on_logout,
    ):
        self.community_id = community_id
        self.summary = summary or {}
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
        sensors = self.summary.get("sensors_summary", {}) or {}
        alerts = self.summary.get("alerts_summary", {}) or {}
        stats = self.summary.get("statistics", {}) or {}

        def tile(title: str, value, subtitle: str = "") -> ft.Container:
            return ft.Container(
                padding=20,
                bgcolor=WHITE,
                border_radius=16,
                content=ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=PRIMARY_GREEN),
                        ft.Text(str(value), size=18, weight=ft.FontWeight.BOLD, color=PRIMARY_GREEN),
                        ft.Text(subtitle, size=11, color=PRIMARY_GREEN) if subtitle else ft.Container(),
                    ],
                ),
            )

        return ft.Column(
            spacing=16,
            controls=[
                ft.Text(
                    f"Panel técnico – Comunidad {self.community_id}",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=PRIMARY_GREEN,
                ),
                tile(
                    "Sensores totales",
                    sensors.get("total_sensors", 0),
                    "Sensores instalados",
                ),
                tile(
                    "Sensores activos",
                    sensors.get("active_sensors", 0),
                    "En funcionamiento (últimas 24h)",
                ),
                tile(
                    "Lecturas últimas 24h",
                    sensors.get("recent_readings_24h", 0),
                    "Actividad de los sensores",
                ),
                tile(
                    "Alertas registradas",
                    alerts.get("total", 0),
                    "En tu comunidad",
                ),
                tile(
                    "Eventos recientes",
                    stats.get("total_events", 0),
                    "Logs asociados al usuario",
                ),
            ],
        )
