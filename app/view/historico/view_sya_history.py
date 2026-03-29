# app/view/historico/view_sya_history.py

import flet as ft

from app.view.base.view_base_dashboard import BaseDashboardView
from app.view.theme import PRIMARY_GREEN, BG_CARD_PRIMARY, WHITE, FULL_BLACK, BRAND_ACCENT_BLUE

from app.repository.reading_repository import ReadingRepository
from app.repository.log_repository import LogRepository
from app.repository.sensor_repository import SensorRepository


class HistoryView(BaseDashboardView):
    '''
    Histórico de sensores y actuadores.
    Filtrado correctamente por comunidad (via sensors).

    '''


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
        self.selected_filter = "SENSORES"  # or ACTUADORES

        self._list_view = ft.Column(
            spacing=12,
            scroll=ft.ScrollMode.ALWAYS,
            controls=[],
        )

        self.community_id = community_id
        self.sensor_repo = SensorRepository()
        self.reading_repo = ReadingRepository()
        self.log_repo = LogRepository()
        self.batch_size = 25  # for pagination
        self.current_limit = self.batch_size

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

    # ============================================================
    # Header tabs
    # ============================================================
    def _filter_chips(self):
        def set_filter(value: str):
            self.selected_filter = value
            self._refresh_list()

            for c in chips.controls:
                c.selected = (c.data == value)
            self.update()

        chips = ft.Row(
            spacing=12,
            controls=[
                ft.Chip(
                    label=ft.Text("Sensores"),
                    data="SENSORES",
                    selected=self.selected_filter == "SENSORES",
                    on_select=lambda e: set_filter(e.control.data),
                ),
                ft.Chip(
                    label=ft.Text("Actuadores"),
                    data="ACTUADORES",
                    selected=self.selected_filter == "ACTUADORES",
                    on_select=lambda e: set_filter(e.control.data),
                ),
            ],
        )
        return chips

    # -----------------------------------------------------------
    # HELPERS
    # ----------------------------------------------------------

    def _build_sensor_items(self):
        sensors = self.sensor_repo.get_all()
        sensors_in_comm = {
            str(s.sensor_id): s
            for s in sensors
            if s.from_community_id == self.community_id
        }

        readings = [
            r for r in self.reading_repo.get_all()
            if str(r.sensor_id) in sensors_in_comm
        ]

        if not readings:
            return [ft.Text("No hay registros de sensores.", size=12, color=FULL_BLACK)]

        readings = sorted(
            readings,
            key=lambda r: r.timestamp,
            reverse=True,
        )[:self.current_limit]

        return [
            self._sensor_entry_tile(r, sensors_in_comm[str(r.sensor_id)])
            for r in readings
        ]


    def _build_actuator_items(self):
        logs = [
            log for log in self.log_repo.all()
            if log.get("category") == "ACTUATOR"
        ]

        logs = sorted(
            logs,
            key=lambda l: l.get("timestamp", ""),
            reverse=True,
        )[:self.current_limit]

        if not logs:
            return [ft.Text("No hay registros de actuadores.", size=12, color=FULL_BLACK)]

        return [self._actuator_log_tile(l) for l in logs]


    def _refresh_list(self):
        if self.selected_filter == "SENSORES":
            self._list_view.controls = self._build_sensor_items()
        else:
            self._list_view.controls = self._build_actuator_items()

        if self._list_view.page:
            self._list_view.update()

    def _load_more(self, e):
        self.current_limit += self.batch_size
        self._refresh_list()


    # ============================================================
    # Tiles
    # ============================================================
    def _sensor_entry_tile(self, entry, sensor):
        if isinstance(entry.value, float):
            value = round(entry.value, 2)
        else:
            value = entry.value
        return ft.Container(
            bgcolor=WHITE,
            border_radius=16,
            padding=12,
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Text(
                        f"{sensor.type} ({sensor.location})",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=PRIMARY_GREEN,
                    ),
                    ft.Text(f"Valor: {value} {entry.unit}", size=12, color=BRAND_ACCENT_BLUE),
                    ft.Text(f"Fecha: {entry.timestamp.strftime('%d-%m-%Y %H:%M:%S')}", size=12, color=FULL_BLACK),
                ],
            ),
        )

    def _actuator_log_tile(self, log):
        return ft.Container(
            bgcolor=WHITE,
            border_radius=16,
            padding=12,
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Text(
                        f"Actuador ID: {log.get('id')}",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=PRIMARY_GREEN,
                    ),
                    ft.Text(
                        f"Acción: {log.get('action')}",
                        size=12,
                        color=BRAND_ACCENT_BLUE,
                    ),
                    ft.Text(
                        f"Fecha: {log.get('timestamp')}",
                        size=12,
                        color=FULL_BLACK,
                    ),
                ],
            ),
        )


    # ============================================================
    # Main body
    # ============================================================
    def build_body(self):
        self._refresh_list()

        controls = [
            self._filter_chips(),
            self._list_view,
        ]

        if self.selected_filter == "SENSORES":
            total_items = len([
                r for r in self.reading_repo.get_all()
                if str(r.sensor_id) in {
                    str(s.sensor_id)
                    for s in self.sensor_repo.get_all()
                    if s.from_community_id == self.community_id
                }
            ])
        else:
            total_items = len([
                log for log in self.log_repo.get_all()
                if log.get("target_id") is not None
            ])


        if self.current_limit < total_items:
            controls.append(
                ft.TextButton(
                    "Cargar más",
                    on_click=self._load_more,
                )
            )

        return ft.Column(spacing=16, controls=controls)

        
