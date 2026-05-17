import flet as ft
from app.view.base.view_base_dashboard import BaseDashboardView
from app.view.theme import BRAND_ACCENT_BLUE, BRAND_DARK_GREY, PRIMARY_GREEN, WHITE


class TechnicianDashboardView(BaseDashboardView):
    def __init__(
        self,
        page,
        controller,
        user,
        role,
        community_id,
        summary: dict | None,
        temp_series: list[dict] | None,
        hum_series: list[dict] | None,
        alert_chart: dict | None,
        actuator_state: dict | None,
        error_summary: dict | None,
        temp_stats: dict | None,
        sensor_options: dict | None,
        on_dashboard,
        on_settings,
        on_alerts,
        on_logout,
    ):
        self.community_id = community_id
        self.summary = summary or {}
        self.temp_series = temp_series or []
        self.hum_series = hum_series or []
        self.alert_chart = alert_chart or {}
        self.actuator_state = actuator_state or {}
        self.error_summary = error_summary or {}
        self.temp_stats = temp_stats or {}
        self.sensor_options = sensor_options or {}
        self._selected_type = "TEMPERATURE"
        self._selected_sensor_id = None
        self._aggregate = False
        self._window = "7d"
        self._aggregate_bucket = "weekday"
        self._series_status = ""
        self._chart_holder = ft.Column()
        self._sensor_dropdown = None
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

    def _card(self, title: str, value: str, subtitle: str = "") -> ft.Control:
        return ft.Container(
            bgcolor=WHITE,
            border_radius=10,
            padding=14,
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Text(title, color=PRIMARY_GREEN, size=12, weight=ft.FontWeight.BOLD),
                    ft.Text(value, color=PRIMARY_GREEN, size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(subtitle, color=PRIMARY_GREEN, size=11) if subtitle else ft.Container(),
                ],
            ),
        )

    def _mini_bar(self, label: str, value: int, max_value: int) -> ft.Control:
        width_factor = 0 if max_value <= 0 else min(1.0, value / max_value)
        return ft.Column(
            spacing=3,
            controls=[
                ft.Text(f"{label}: {value}", size=11, color=PRIMARY_GREEN),
                ft.Container(
                    height=8,
                    bgcolor="#DDE5E4",
                    border_radius=5,
                    content=ft.Row(
                        spacing=0,
                        controls=[ft.Container(width=220 * width_factor, height=8, bgcolor=PRIMARY_GREEN, border_radius=5)],
                    ),
                ),
            ],
        )

    def _get_current_sensor_options(self):
        return self.sensor_options.get(self._selected_type, []) or []

    def _ensure_selected_sensor(self):
        options = self._get_current_sensor_options()
        if not options:
            self._selected_sensor_id = None
            return
        valid_ids = {int(x["sensor_id"]) for x in options}
        if self._selected_sensor_id not in valid_ids:
            self._selected_sensor_id = int(options[0]["sensor_id"])

    def _build_chart(self) -> ft.Control:
        self._ensure_selected_sensor()
        if self._selected_sensor_id is None:
            return ft.Text("No sensors available for selected type.", color=PRIMARY_GREEN, size=12)

        aggregate_bucket = "hour_2" if self._window == "24h" else "weekday"
        series = self.controller.get_sensor_series_for_dashboard(
            sensor_id=int(self._selected_sensor_id),
            aggregate=self._aggregate,
            window=self._window,
            aggregate_bucket=aggregate_bucket,
        )
        if not series:
            return ft.Text("No data in selected window.", color=PRIMARY_GREEN, size=12)

        values = [float(item["value"]) for item in series]
        raw_min = min(values)
        raw_max = max(values)
        spread = max(0.5, raw_max - raw_min)
        min_y = raw_min - spread * 0.15
        max_y = raw_max + spread * 0.15

        def _y_axis():
            step = (max_y - min_y) / 4.0
            labels = []
            for i in range(5):
                v = min_y + step * i
                labels.append(
                    ft.ChartAxisLabel(
                        value=v,
                        label=ft.Text(f"{v:.1f}", size=10, color=PRIMARY_GREEN),
                    )
                )
            return ft.ChartAxis(labels=labels, labels_size=32, title=ft.Text("Value", size=11, color=PRIMARY_GREEN))

        def _unit_label() -> str:
            if self._selected_type == "HUMIDITY":
                return "%"
            if self._selected_type == "TEMPERATURE":
                return "C"
            return ""

        def _point_tooltip(item: dict, idx: int) -> str:
            label = str(item.get("bucket") or item.get("timestamp") or idx).replace("T", " ")[:19]
            suffix = _unit_label()
            value = float(item["value"])
            return f"{label}\n{self._selected_type}: {value:.2f}{suffix}"

        def _x_axis():
            if not series:
                return ft.ChartAxis()
            n = len(series)
            if self._aggregate:
                idxs = list(range(n))
            else:
                step = max(1, n // 8)
                idxs = sorted(set(list(range(0, n, step)) + [n - 1]))
            labels = []
            for idx in idxs:
                if self._aggregate:
                    text = str(series[idx].get("bucket", ""))
                else:
                    ts = str(series[idx].get("timestamp", ""))
                    text = ts[5:16].replace("T", " ")
                labels.append(
                    ft.ChartAxisLabel(
                        value=float(idx),
                        label=ft.Text(text, size=10, color=PRIMARY_GREEN),
                    )
                )
            return ft.ChartAxis(labels=labels, labels_size=48, title=ft.Text("Time", size=11, color=PRIMARY_GREEN))

        if self._aggregate:
            points = [
                ft.LineChartDataPoint(
                    x=float(i),
                    y=float(item["value"]),
                    tooltip=_point_tooltip(item, i),
                )
                for i, item in enumerate(series)
            ]
            self._series_status = f"Mode: aggregated | Bucket: {aggregate_bucket} | Window: {self._window} | Min/Max: {raw_min:.2f}/{raw_max:.2f}"
            return ft.LineChart(
                data_series=[ft.LineChartData(data_points=points, curved=True, stroke_width=3, point=True)],
                min_y=min_y,
                max_y=max_y,
                min_x=0,
                max_x=max(1, len(points) - 1),
                left_axis=_y_axis(),
                bottom_axis=_x_axis(),
                height=220,
                expand=True,
                interactive=True,
                tooltip_bgcolor="#EAF4F2",
            )

        points = [
            ft.LineChartDataPoint(
                x=float(i),
                y=float(item["value"]),
                tooltip=_point_tooltip(item, i),
            )
            for i, item in enumerate(series)
        ]
        first_ts = series[0].get("timestamp")
        last_ts = series[-1].get("timestamp")
        self._series_status = (
            f"Mode: raw samples | Window: {self._window} | "
            f"Range: {str(first_ts)[:16]} -> {str(last_ts)[:16]} | Min/Max: {raw_min:.2f}/{raw_max:.2f}"
        )
        return ft.LineChart(
            data_series=[ft.LineChartData(data_points=points, curved=False, stroke_width=1, point=True)],
            min_y=min_y,
            max_y=max_y,
            min_x=0,
            max_x=max(1, len(points) - 1),
            left_axis=_y_axis(),
            bottom_axis=_x_axis(),
            height=220,
            expand=True,
            interactive=True,
            tooltip_bgcolor="#EAF4F2",
        )

    def _refresh_chart(self):
        self._chart_holder.controls = [self._build_chart(), ft.Text(self._series_status, size=11, color=PRIMARY_GREEN)]
        self.update()

    def build_body(self) -> ft.Control:
        sensors = self.summary.get("sensors_summary", {}) or {}
        by_sev = self.alert_chart.get("by_severity", {}) or {}
        max_sev = max(by_sev.values()) if by_sev else 0
        temp_avg = self.temp_stats.get("avg")

        return ft.Column(
            spacing=14,
            controls=[
                ft.Text(f"Technician Panel - Community {self.community_id}", size=20, weight=ft.FontWeight.BOLD, color=PRIMARY_GREEN),
                ft.Row(
                    spacing=10,
                    controls=[
                        self._card("Active Sensors", str(sensors.get("active_sensors", 0)), "Current community"),
                        self._card("Readings 24h", str(sensors.get("recent_readings_24h", 0)), "Telemetry volume"),
                        self._card("Errors 7d", str(self.error_summary.get("total", 0)), "Technical incidents"),
                    ],
                ),
                self._card(
                    "Temperature Avg (24h)",
                    f"{round(temp_avg, 2) if temp_avg is not None else '--'} C",
                    f"Min {self.temp_stats.get('min')} / Max {self.temp_stats.get('max')}",
                ),
                ft.Container(
                    bgcolor=WHITE,
                    border_radius=10,
                    padding=14,
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Text("Alerts by severity (7d)", color=PRIMARY_GREEN, weight=ft.FontWeight.BOLD),
                            self._mini_bar("CRIT", int(by_sev.get("CRIT", 0)), max_sev),
                            self._mini_bar("WARN", int(by_sev.get("WARN", 0)), max_sev),
                            self._mini_bar("INFO", int(by_sev.get("INFO", 0)), max_sev),
                        ],
                    ),
                ),
                self._card(
                    "Actuators ON/OFF",
                    f"{self.actuator_state.get('on', 0)} / {self.actuator_state.get('off', 0)}",
                    f"Total {self.actuator_state.get('total', 0)}",
                ),
                ft.Container(
                    bgcolor=WHITE,
                    border_radius=10,
                    padding=14,
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Text("Sensor detail chart", color=PRIMARY_GREEN, weight=ft.FontWeight.BOLD),
                            ft.Row(
                                spacing=10,
                                controls=[
                                    ft.Dropdown(
                                        width=170,
                                        label="Type",
                                        label_style=ft.TextStyle(color=BRAND_ACCENT_BLUE),
                                        value=self._selected_type,
                                        options=[
                                            ft.dropdown.Option(key="TEMPERATURE", text="TEMPERATURE"),
                                            ft.dropdown.Option(key="HUMIDITY", text="HUMIDITY"),
                                            ft.dropdown.Option(key="WIND", text="WIND"),
                                        ],
                                        on_change=lambda e: self._on_type_change(e),
                                    ),
                                    ft.Dropdown(
                                        width=350,
                                        label="Sensor",
                                        label_style=ft.TextStyle(color=BRAND_ACCENT_BLUE),
                                        options=[
                                            ft.dropdown.Option(key=str(item["sensor_id"]), text=item["label"])
                                            for item in self._get_current_sensor_options()
                                        ],
                                        value=str(self._selected_sensor_id) if self._selected_sensor_id is not None else None,
                                        on_change=lambda e: self._on_sensor_change(e),
                                        ref=ft.Ref[ft.Dropdown]()
                                    ),
                                    ft.Switch(
                                        label="Aggregated",
                                        label_style=ft.TextStyle(color=BRAND_DARK_GREY),
                                        value=self._aggregate,
                                        on_change=lambda e: self._on_toggle_aggregate(e),
                                    ),
                                    ft.Dropdown(
                                        width=120,
                                        label="Window",
                                        value=self._window,
                                        options=[
                                            ft.dropdown.Option(key="24h", text="24h"),
                                            ft.dropdown.Option(key="7d", text="7d"),
                                        ],
                                        on_change=lambda e: self._on_window_change(e),
                                    ),
                                ],
                            ),
                            self._chart_holder,
                        ],
                    ),
                ),
            ],
        )

    def did_mount(self):
        self._ensure_selected_sensor()
        self._refresh_chart()

    def _on_type_change(self, e):
        self._selected_type = str(e.control.value)
        self._selected_sensor_id = None
        # Rebuild whole dashboard to refresh dependent dropdown options safely.
        self.controller.show_tecnico_dashboard()
        return
        self._refresh_chart()

    def _on_sensor_change(self, e):
        self._selected_sensor_id = int(e.control.value)
        self._refresh_chart()

    def _on_toggle_aggregate(self, e):
        self._aggregate = bool(e.control.value)
        self._refresh_chart()

    def _on_window_change(self, e):
        self._window = str(e.control.value)
        self._refresh_chart()
