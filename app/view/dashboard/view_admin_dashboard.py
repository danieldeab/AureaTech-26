# app/view/dashboard/view_admin_dashboard.py

import flet as ft
from app.view.base.view_base_dashboard import BaseDashboardView
from app.view.theme import PRIMARY_GREEN, WHITE, BRAND_ACCENT_BLUE, BRAND_LIGHT_GREY, TEXT_SECONDARY


class AdminDashboardView(BaseDashboardView):
    """
    Dashboard for ADMIN users.

    It expects a `summary` dict coming from DashboardService.get_dashboard_summary(...).to_dict()
    and shows basic community-level stats.
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
            on_back=None,
        )

    def _build_kpis(self):
        
        kpis = self.controller.get_kpis()
        streetlights_on = kpis["streetlights_on"]
        streetlights_total = kpis["streetlights_total"]
        
        progress = (
            streetlights_on / streetlights_total
            if streetlights_total > 0 else 0
        )

        active_alerts = kpis["active_alerts"]
        automation_events = kpis["automation_events"]
        last_event_ts = kpis["last_event"] or "N/A"

        return ft.Column(
            controls=[
                ft.Text(
                    "System Overview",
                    size=20,
                    weight="bold",
                    color=PRIMARY_GREEN,
                ),

                ft.Row(
                    spacing=24,
                    controls=[
                        # LEFT HALF — Streetlights
                        ft.Container(
                            expand=1,
                            content=ft.Column(
                                spacing=8,
                                controls=[
                                    ft.Text("Streetlights ON", color=PRIMARY_GREEN),
                                    ft.ProgressBar(
                                        value=progress,
                                        height=6,
                                        bgcolor=BRAND_LIGHT_GREY,
                                        color=BRAND_ACCENT_BLUE,
                                    ),
                                    ft.Text(f"{streetlights_on} / {streetlights_total}", color=BRAND_ACCENT_BLUE),
                                ],
                            ),
                        ),

                        # RIGHT HALF — Alerts + Automation
                        ft.Container(
                            expand=1,
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                                spacing=12,
                                controls=[
                                    ft.Column(
                                        controls=[
                                            ft.Text("Active Alerts", color=PRIMARY_GREEN),
                                            ft.Text(
                                                str(active_alerts),
                                                size=24,
                                                weight="bold",
                                                color=BRAND_ACCENT_BLUE,
                                            ),
                                        ]
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text("Automation Events", color=PRIMARY_GREEN),
                                            ft.Text(
                                                str(automation_events),
                                                size=24,
                                                weight="bold",
                                                color=BRAND_ACCENT_BLUE,
                                            ),
                                        ]
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),

                ft.Text(
                    f"Last system event: {last_event_ts}",
                    size=12,
                    color=TEXT_SECONDARY,
                ),
            ]
        )


    def build_body(self) -> ft.Control:

        # community selection dropdown
        # Discover existing communities from summary
        communities = self.summary.get("available_communities", [])

        if self.community_id is None and communities:
            self.community_id = communities[0]


        # Dropdown should reflect current selection
        dropdown = ft.Dropdown(
            label="Seleccionar comunidad",
            width=300,
            color=PRIMARY_GREEN,
            focused_color=WHITE,
            options=[ft.dropdown.Option(str(c)) for c in communities],
            value=str(self.community_id) if self.community_id is not None else None,
            on_change=lambda e: self.controller.set_selected_community(int(e.control.value))
        )

        header_section = ft.Column(
            spacing=10,
            controls=[
                ft.Text(
                    "Panel de Administración",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=PRIMARY_GREEN,
                ),
                dropdown,
            ]
        )


        # Safely unpack the pieces of the summary
        sensors = self.summary.get("sensors_summary", {}) or {}
        acts = self.summary.get("actuators_summary", {}) or {}
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
                self._build_kpis(),
                ft.Text(
                    f"Panel de administración – Comunidad {self.community_id}",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=PRIMARY_GREEN,
                ),
                header_section,
                tile(
                    "Sensores totales",
                    sensors.get("total_sensors", 0),
                    "Sensores registrados en la comunidad",
                ),
                tile(
                    "Sensores activos",
                    sensors.get("active_sensors", 0),
                    "En funcionamiento (últimas 24h)",
                ),
                tile(
                    "Actuadores totales",
                    acts.get("total_actuators", 0),
                    "Actuadores registrados",
                ),
                tile(
                    "Actuadores activos",
                    acts.get("active_actuators", 0),
                    "En uso actualmente",
                ),
                tile(
                    "Alertas registradas",
                    alerts.get("total", 0),
                    "De cualquier severidad",
                ),
                tile(
                    "Eventos recientes",
                    stats.get("total_events", 0),
                    "Entradas de log recientes",
                ),
            ],
        )
