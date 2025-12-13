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
        self.active_tab = "sensores"

        self.community_id = community_id
        self.sensor_repo = SensorRepository()
        self.reading_repo = ReadingRepository()
        self.log_repo = LogRepository()

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
    def _tabs(self):
        def activate(tab):
            self.active_tab = tab
            self.page.update()

        return ft.Row(
            alignment=ft.MainAxisAlignment.START,
            spacing=20,
            controls=[
                ft.TextButton(
                    "Histórico de sensores",
                    on_click=lambda e: activate("sensores"),
                    style=ft.ButtonStyle(
                        color=PRIMARY_GREEN if self.active_tab == "sensores" else FULL_BLACK
                    ),
                ),
                ft.TextButton(
                    "Histórico de actuadores",
                    on_click=lambda e: activate("actuadores"),
                    style=ft.ButtonStyle(
                        color=PRIMARY_GREEN if self.active_tab == "actuadores" else FULL_BLACK
                    ),
                ),
            ],
        )

    # ============================================================
    # Tiles
    # ============================================================
    def _sensor_entry_tile(self, entry, sensor):
        if entry.isnumeric():
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
                        f"Actuador ID: {log.actuator_id}",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=PRIMARY_GREEN,
                    ),
                    ft.Text(f"Acción: {log.message}", size=12),
                    ft.Text(f"Fecha: {log.timestamp}", size=12),
                ],
            ),
        )

    # ============================================================
    # Main body
    # ============================================================
    def build_body(self):
        tabs = self._tabs()

        # Build community sensor map
        sensors = self.sensor_repo.get_all()
        sensors_in_comm = {
            str(s.id): s
            for s in sensors
            if s.community_id == self.community_id
        }

        if self.active_tab == "sensores":
            # Filter readings belonging to these sensors
            readings = [
                r for r in self.reading_repo.get_all()
                if str(r.sensor_id) in sensors_in_comm
            ]

            items = (
                [
                    self._sensor_entry_tile(r, sensors_in_comm[str(r.sensor_id)])
                    for r in readings
                ]
                if readings else
                [ft.Text("No hay registros de sensores.", size=12)]
            )

        else:  # histórico de actuadores
            logs = []

            # Show only logs that clearly contain actuator actions
            for log in self.log_repo.get_all():
                if getattr(log, "actuator_id", None) is not None:
                    logs.append(log)

            items = (
                [self._actuator_log_tile(l) for l in logs]
                if logs else
                [ft.Text("No hay registros de actuadores.", size=12)]
            )

        return ft.Column(
            spacing=16,
            controls=[
                tabs,
                ft.Column(
                    spacing=12,
                    scroll=ft.ScrollMode.ALWAYS,
                    controls=items,
                ),
            ],
        )
