import flet as ft
from app.view.base.view_base_dashboard import BaseDashboardView
from app.view.theme import BRAND_ACCENT_BLUE, BRAND_DARK_GREY, BTN_DANGER_BG, PRIMARY_GREEN, WHITE


class AdminDashboardView(BaseDashboardView):
    def __init__(
        self,
        page,
        controller,
        user,
        role,
        community_id,
        summary: dict | None,
        all_communities_overview: list[dict] | None,
        sensitive_summary: dict | None,
        temp_line_series: list[dict] | None,
        hum_line_series: list[dict] | None,
        on_dashboard,
        on_settings,
        on_alerts,
        on_logout,
        aggregation_period: str = "7d",
    ):
        self.community_id = community_id
        self.summary = summary or {}
        self.all_communities_overview = all_communities_overview or []
        self.sensitive_summary = sensitive_summary or {"total": 0, "by_community": {}}
        self.temp_line_series = temp_line_series or []
        self.hum_line_series = hum_line_series or []
        self.aggregation_period = aggregation_period
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

    def _metric(self, title: str, value: str, subtitle: str = "") -> ft.Control:
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
                    ft.Text(subtitle, size=11, color=PRIMARY_GREEN) if subtitle else ft.Container(),
                ],
            ),
        )

    def build_body(self) -> ft.Control:
        communities = self.summary.get("available_communities", [])
        dropdown = ft.Dropdown(
            label="Community",
            label_style=ft.TextStyle(color=PRIMARY_GREEN),
            width=300,
            options=[ft.dropdown.Option(str(c)) for c in communities],
            value=str(self.community_id) if self.community_id is not None else None,
            on_change=lambda e: self.controller.set_selected_community(int(e.control.value)),
            color=PRIMARY_GREEN,
            focused_color=BRAND_ACCENT_BLUE,
            autofocus=True,
            bgcolor=WHITE,
            hint_style=ft.TextStyle(color=PRIMARY_GREEN, italic=True),
        )

        total_unknown = int(self.sensitive_summary.get("total", 0))
        total_alerts = sum(int(r.get("alerts_7d", 0)) for r in self.all_communities_overview)
        total_errors = sum(int(r.get("errors_7d", 0)) for r in self.all_communities_overview)

        rows = []
        for row in self.all_communities_overview:
            unknown_plates = int(row.get("unknown_plates_7d", 0))
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row.get("community_id")), color=BRAND_DARK_GREY, weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(str(row.get("sensors", 0)), color=BRAND_DARK_GREY)),
                        ft.DataCell(ft.Text(str(row.get("alerts_7d", 0)), color=BRAND_DARK_GREY)),
                        ft.DataCell(ft.Text(str(row.get("errors_7d", 0)), color=BRAND_DARK_GREY)),
                        ft.DataCell(
                            ft.Container(
                                bgcolor=BTN_DANGER_BG if unknown_plates > 0 else None,
                                padding=8,
                                border_radius=6,
                                content=ft.Text(str(unknown_plates), color=BRAND_DARK_GREY),
                            ),
                        ),
                    ],
                )
            )

        def _line(series: list[dict], label: str) -> ft.Control:
            if not series:
                return ft.Text(f"{label}: no data", size=11, color=PRIMARY_GREEN)
            points = [ft.LineChartDataPoint(x=float(i), y=float(item["value"])) for i, item in enumerate(series)]
            first_bucket = series[0].get("bucket", "")
            last_bucket = series[-1].get("bucket", "")
            values = [float(item["value"]) for item in series]
            raw_min = min(values)
            raw_max = max(values)
            spread = max(0.5, raw_max - raw_min)
            min_y = raw_min - spread * 0.15
            max_y = raw_max + spread * 0.15

            step = (max_y - min_y) / 4.0
            y_labels = []
            for i in range(5):
                v = min_y + step * i
                y_labels.append(
                    ft.ChartAxisLabel(
                        value=v,
                        label=ft.Text(f"{v:.1f}", size=10, color=PRIMARY_GREEN),
                    )
                )

            n = len(series)
            idxs = sorted({0, max(0, n // 2), n - 1})
            x_labels = []
            for idx in idxs:
                raw_label = str(series[idx].get("bucket", ""))
                if len(raw_label) > 12:
                    raw_label = raw_label[:12]
                x_labels.append(
                    ft.ChartAxisLabel(
                        value=float(idx),
                        label=ft.Text(raw_label, size=9, color=PRIMARY_GREEN),
                    )
                )
            return ft.Column(
                spacing=4,
                controls=[
                    ft.Text(label, color=PRIMARY_GREEN, size=12, weight=ft.FontWeight.BOLD),
                    ft.LineChart(
                        data_series=[ft.LineChartData(data_points=points, curved=True, stroke_width=3)],
                        min_y=min_y,
                        max_y=max_y,
                        min_x=0,
                        max_x=max(1, len(points) - 1),
                        left_axis=ft.ChartAxis(
                            labels=y_labels,
                            labels_size=32,
                            title=ft.Text("Value", size=11, color=PRIMARY_GREEN),
                        ),
                        bottom_axis=ft.ChartAxis(
                            labels=x_labels,
                            labels_size=72,
                            title=ft.Text("Date", size=11, color=PRIMARY_GREEN),
                        ),
                        height=240,
                    ),
                    ft.Text(
                        f"Aggregated by {'2-hour bucket' if self.aggregation_period == '24h' else 'weekday'} | Window: {self.aggregation_period} | Range: {first_bucket} -> {last_bucket} | Min/Max: {raw_min:.2f}/{raw_max:.2f}",
                        size=10,
                        color=PRIMARY_GREEN,
                    ),
                ],
            )

        return ft.Column(
            spacing=14,
            controls=[
                ft.Text("Admin Control Center", size=20, weight=ft.FontWeight.BOLD, color=PRIMARY_GREEN),
                dropdown,
                ft.Row(
                    spacing=10,
                    controls=[
                        self._metric("Alerts 7d (all)", str(total_alerts), "All communities"),
                        self._metric("Errors 7d (all)", str(total_errors), "All communities"),
                        self._metric("Unknown plates 7d", str(total_unknown), "Sensitive indicator"),
                    ],
                ),
                ft.Container(
                    bgcolor=WHITE,
                    border_radius=10,
                    padding=12,
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Text("Cross-community overview", color=PRIMARY_GREEN, weight=ft.FontWeight.BOLD, size=15),
                            ft.DataTable(
                                columns=[
                                    ft.DataColumn(ft.Text("Community", color=PRIMARY_GREEN, weight=ft.FontWeight.BOLD)),
                                    ft.DataColumn(ft.Text("Sensors", color=PRIMARY_GREEN, weight=ft.FontWeight.BOLD)),
                                    ft.DataColumn(ft.Text("Alerts 7d", color=PRIMARY_GREEN, weight=ft.FontWeight.BOLD)),
                                    ft.DataColumn(ft.Text("Errors 7d", color=PRIMARY_GREEN, weight=ft.FontWeight.BOLD)),
                                    ft.DataColumn(ft.Text("Unknown plates 7d", color=PRIMARY_GREEN, weight=ft.FontWeight.BOLD)),
                                ],
                                rows=rows,
                            ),
                        ],
                    ),
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    bgcolor=WHITE,
                    border_radius=10,
                    padding=12,
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Text("Aggregated weekly trend (selected community)", color=PRIMARY_GREEN, weight=ft.FontWeight.BOLD),
                            ft.Row(
                                spacing=10,
                                controls=[
                                    ft.Dropdown(
                                        width=180,
                                        label="Aggregation",
                                        value=self.aggregation_period,
                                        options=[
                                            ft.dropdown.Option(key="24h", text="Day (24h)"),
                                            ft.dropdown.Option(key="7d", text="Week (7d)"),
                                        ],
                                        on_change=lambda e: self.controller.set_admin_chart_options(period=e.control.value),
                                    ),
                                ],
                            ),
                            _line(self.temp_line_series, "Temperature"),
                            _line(self.hum_line_series, "Humidity"),
                        ],
                    ),
                ),
            ],
        )
