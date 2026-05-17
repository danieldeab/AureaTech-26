import flet as ft
from app.view.base.view_base_dashboard import BaseDashboardView
from app.view.theme import PRIMARY_GREEN, WHITE


class UserDashboardView(BaseDashboardView):
    def __init__(
        self,
        page,
        controller,
        user,
        role,
        on_dashboard,
        on_settings,
        on_alerts,
        on_logout,
        community_id,
        summary: dict | None = None,
        temp_series: list[dict] | None = None,
        hum_series: list[dict] | None = None,
        alerts_data: dict | None = None,
        latest_temp: dict | None = None,
        latest_hum: dict | None = None,
        latest_smoke: dict | None = None,
        week_temp_stats: dict | None = None,
        month_temp_stats: dict | None = None,
        week_hum_stats: dict | None = None,
        month_hum_stats: dict | None = None,
        plate_history: list[dict] | None = None,
    ):
        self.community_id = community_id
        self.summary = summary or {}
        self.temp_series = temp_series or []
        self.hum_series = hum_series or []
        self.alerts_data = alerts_data or {}
        self.latest_temp = latest_temp or {}
        self.latest_hum = latest_hum or {}
        self.latest_smoke = latest_smoke or {}
        self.week_temp_stats = week_temp_stats or {}
        self.month_temp_stats = month_temp_stats or {}
        self.week_hum_stats = week_hum_stats or {}
        self.month_hum_stats = month_hum_stats or {}
        self.plate_history = plate_history or []
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

    def _metric(self, title: str, value: str) -> ft.Control:
        return ft.Container(
            expand=True,
            bgcolor=WHITE,
            border_radius=10,
            padding=14,
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Text(title, size=12, color=PRIMARY_GREEN, weight=ft.FontWeight.BOLD),
                    ft.Text(value, size=18, color=PRIMARY_GREEN, weight=ft.FontWeight.BOLD),
                ],
            ),
        )

    def _latest(self, series: list[dict], default: str = "--") -> str:
        if not series:
            return default
        return str(series[-1].get("value", default))

    def build_body(self) -> ft.Control:
        sensors = self.summary.get("sensors_summary", {}) or {}
        latest_temp = self.latest_temp.get("value", self._latest(self.temp_series))
        latest_hum = self.latest_hum.get("value", self._latest(self.hum_series))
        latest_smoke = self.latest_smoke.get("value", "--")
        alerts_total = self.alerts_data.get("total", 0)
        unread = self.summary.get("alerts_summary", {}).get("unread", 0)

        def _bar_pair(title: str, week: float | None, month: float | None, unit: str) -> ft.Control:
            week_val = 0 if week is None else float(week)
            month_val = 0 if month is None else float(month)
            max_val = max(week_val, month_val, 1)
            return ft.Container(
                bgcolor=WHITE,
                border_radius=10,
                padding=12,
                content=ft.Column(
                    spacing=6,
                    controls=[
                        ft.Text(title, color=PRIMARY_GREEN, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Week: {round(week_val, 2)} {unit}", size=11, color=PRIMARY_GREEN),
                        ft.Container(height=8, bgcolor="#DDE5E4", border_radius=6, content=ft.Container(width=240 * (week_val / max_val), bgcolor=PRIMARY_GREEN, border_radius=6)),
                        ft.Text(f"Month: {round(month_val, 2)} {unit}", size=11, color=PRIMARY_GREEN),
                        ft.Container(height=8, bgcolor="#DDE5E4", border_radius=6, content=ft.Container(width=240 * (month_val / max_val), bgcolor="#4A7F77", border_radius=6)),
                    ],
                ),
            )

        plate_rows = []
        for item in self.plate_history[:8]:
            plate_rows.append(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(item.get("plate", "--"), size=12, color=PRIMARY_GREEN),
                        ft.Text((item.get("detected_at") or "")[:16].replace("T", " "), size=11, color=PRIMARY_GREEN),
                    ],
                )
            )

        return ft.Column(
            spacing=16,
            controls=[
                ft.Text("My Community Overview", size=20, weight=ft.FontWeight.BOLD, color=PRIMARY_GREEN),
                ft.Row(
                    spacing=10,
                    controls=[
                        self._metric("Temperature", f"{latest_temp} C"),
                        self._metric("Humidity", f"{latest_hum} %"),
                        self._metric("Smoke", f"{latest_smoke} ppm"),
                    ],
                ),
                ft.Text(
                    f"Last update: {str(self.latest_temp.get('timestamp', '--')).replace('T', ' ')[:16]}",
                    size=11,
                    color=PRIMARY_GREEN,
                ),
                ft.Row(
                    spacing=10,
                    controls=[
                        self._metric("Sensors Active", str(sensors.get("active_sensors", 0))),
                        self._metric("Alerts (7d)", str(alerts_total)),
                    ],
                ),
                ft.Container(
                    bgcolor=WHITE,
                    border_radius=10,
                    padding=14,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Unread alerts", color=PRIMARY_GREEN, weight=ft.FontWeight.BOLD),
                            ft.Text(str(unread), color=PRIMARY_GREEN, size=18, weight=ft.FontWeight.BOLD),
                        ],
                    ),
                ),
                _bar_pair(
                    "Temperature average comparison",
                    self.week_temp_stats.get("avg"),
                    self.month_temp_stats.get("avg"),
                    "C",
                ),
                _bar_pair(
                    "Humidity average comparison",
                    self.week_hum_stats.get("avg"),
                    self.month_hum_stats.get("avg"),
                    "%",
                ),
                ft.Container(
                    bgcolor=WHITE,
                    border_radius=10,
                    padding=12,
                    content=ft.Column(
                        spacing=6,
                        controls=[ft.Text("Recent plate entries", color=PRIMARY_GREEN, weight=ft.FontWeight.BOLD)]
                        + (plate_rows if plate_rows else [ft.Text("No entries yet.", size=11, color=PRIMARY_GREEN)]),
                    ),
                ),
            ],
        )
