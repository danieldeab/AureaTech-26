import flet as ft

from app.repository.log_repository import LogRepository
from app.repository.reading_repository import ReadingRepository
from app.repository.sensor_repository import SensorRepository
from app.view.base.view_base_dashboard import BaseDashboardView
from app.view.theme import BRAND_ACCENT_BLUE, FULL_BLACK, PRIMARY_GREEN, WHITE


class HistoryView(BaseDashboardView):
    def __init__(
        self,
        page: ft.Page,
        controller,
        user,
        role: str,
        community_id: int,
        on_dashboard,
        on_alerts,
        on_logout,
        on_settings,
    ):
        self.selected_filter = "SENSORES"
        self.community_id = community_id
        self.sensor_repo = SensorRepository()
        self.reading_repo = ReadingRepository()
        self.log_repo = LogRepository()
        self.batch_size = 25
        self.current_limit = self.batch_size
        self._list_view = ft.Column(spacing=12, scroll=ft.ScrollMode.ALWAYS, controls=[])

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

    def _filter_chips(self):
        def set_filter(value: str):
            self.selected_filter = value
            self.current_limit = self.batch_size
            self._refresh_list()
            for chip in chips.controls:
                chip.selected = chip.data == value
            self.update()

        chips = ft.Row(
            spacing=12,
            controls=[
                ft.Chip(
                    label=ft.Text("Sensores"),
                    selected=self.selected_filter == "SENSORES",
                    data="SENSORES",
                    on_select=lambda e: set_filter(e.control.data),
                ),
                ft.Chip(
                    label=ft.Text("Actuadores"),
                    selected=self.selected_filter == "ACTUADORES",
                    data="ACTUADORES",
                    on_select=lambda e: set_filter(e.control.data),
                ),
            ],
        )
        return chips

    def _build_sensor_items(self):
        sensors_in_comm = {
            str(s.sensor_id): s
            for s in self.sensor_repo.get_all()
            if s.from_community_id == self.community_id
        }
        readings = self.reading_repo.search(
            {"community_id": self.community_id},
            limit=self.current_limit,
        )
        rows = [
            self._sensor_entry_tile(r, sensors_in_comm[str(r.sensor_id)])
            for r in readings
            if str(r.sensor_id) in sensors_in_comm
        ]
        return rows or [ft.Text("No hay registros de sensores.", size=12, color=FULL_BLACK)]

    def _build_actuator_items(self):
        logs = self.log_repo.search(
            {"category": "ACTUATOR", "community_id": self.community_id},
            limit=self.current_limit,
        )
        return [self._actuator_log_tile(l) for l in logs] or [
            ft.Text("No hay registros de actuadores.", size=12, color=FULL_BLACK)
        ]

    def _refresh_list(self):
        self._list_view.controls = (
            self._build_sensor_items()
            if self.selected_filter == "SENSORES"
            else self._build_actuator_items()
        )
        if self._list_view.page:
            self._list_view.update()

    def _load_more(self, e):
        self.current_limit += self.batch_size
        self._refresh_list()
        self.update()

    def _sensor_entry_tile(self, entry, sensor):
        value = round(entry.value, 2) if isinstance(entry.value, float) else entry.value
        return ft.Container(
            bgcolor=WHITE,
            border_radius=12,
            padding=12,
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Text(f"{sensor.type} ({sensor.location})", size=14, weight=ft.FontWeight.BOLD, color=PRIMARY_GREEN),
                    ft.Text(f"Valor: {value} {entry.unit}", size=12, color=BRAND_ACCENT_BLUE),
                    ft.Text(f"Fecha: {entry.timestamp.strftime('%d-%m-%Y %H:%M:%S')}", size=12, color=FULL_BLACK),
                ],
            ),
        )

    def _actuator_log_tile(self, log):
        metadata = log.get("metadata") or {}
        return ft.Container(
            bgcolor=WHITE,
            border_radius=12,
            padding=12,
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Text(
                        f"Actuador ID: {metadata.get('target_entity_id', '--')}",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=PRIMARY_GREEN,
                    ),
                    ft.Text(f"Accion: {log.get('event_type', '--')}", size=12, color=BRAND_ACCENT_BLUE),
                    ft.Text(f"Detalle: {log.get('description', '')}", size=12, color=FULL_BLACK),
                    ft.Text(f"Fecha: {log.get('ts', '--')}", size=12, color=FULL_BLACK),
                ],
            ),
        )

    def build_body(self):
        self._refresh_list()
        controls = [self._filter_chips(), self._list_view]
        if len(self._list_view.controls) >= self.current_limit:
            controls.append(ft.TextButton("Cargar mas", on_click=self._load_more))
        return ft.Column(spacing=16, controls=controls)
