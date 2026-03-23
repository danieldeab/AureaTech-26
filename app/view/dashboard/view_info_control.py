# app/view/dashboard/view_info_control.py

import flet as ft

from app.view.base.view_base_dashboard import BaseDashboardView
from app.view.theme import BRAND_ACCENT_BLUE, PRIMARY_GREEN, WHITE, BG_CARD_PRIMARY, FULL_BLACK, BRAND_LIGHT_GREY

from app.service.sensor_service import SensorService
from app.service.actuator_service import ActuatorService
from app.repository.sensor_repository import SensorRepository
from app.repository.reading_repository import ReadingRepository
from app.repository.actuator_repository import ActuatorRepository
from app.model.enums import RoleEnum


class InfoControlView(BaseDashboardView):
    """
    Combined view for:
    - Sensors info (left column)
    - Actuators control (right column, with toggles)

    Used by TECHNICIAN and ADMIN roles.
    `community_id` is the community whose infrastructure is being inspected.
    """

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
        self.community_id = community_id

        # Services for data access
        self.sensor_service = SensorService(SensorRepository(), ReadingRepository())
        self.actuator_service = ActuatorService(ActuatorRepository())

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

    # -------------------------------------------------------
    # Helpers to render tiles
    # -------------------------------------------------------

    def _sensor_tile(self, sensor) -> ft.Control:
        """
        Simple card with sensor info.
        You can enrich this later (last reading, thresholds, etc.).
        """
        title = f"{sensor.type} ({sensor.location})"

        threshold_texts = []
        for name, value in (sensor.thresholds or {}).items():
            threshold_texts.append(f"- {name}: {value}")

        if not threshold_texts:
            threshold_texts.append("- Sin umbrales definidos")

        return ft.Container(
            bgcolor=WHITE,
            border_radius=16,
            padding=12,
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=PRIMARY_GREEN),
                    *[ft.Text(t, size=12, color=FULL_BLACK) for t in threshold_texts],
                ],
            ),
        )

    def _actuator_tile(self, actuator) -> ft.Control:
        """
        Card with actuator info and ON/OFF toggle.
        """
        title = f"{actuator.name} (Comunidad {actuator.community_id})"

        def _on_toggle(e: ft.ControlEvent):
            new_state = e.control.value
            # Delegate to service (permissions based on user role & community)
            self._toggle_actuator(actuator.id, new_state)

        switch = ft.Switch(
            value=actuator.state,
            active_color=BRAND_ACCENT_BLUE,
            on_change=_on_toggle,
        )

        return ft.Container(
            bgcolor=WHITE,
            border_radius=16,
            padding=12,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=PRIMARY_GREEN),
                            ft.Text(
                                "Control remoto del actuador",
                                size=12,
                                color=FULL_BLACK,
                            ),
                        ],
                    ),
                    switch,
                ],
            ),
        )

    def _toggle_actuator(self, actuator_id, new_state: bool):
        """
        Use ActuatorService to toggle actuator safely.
        """
        try:
            role_enum = self.user.role if isinstance(self.user.role, RoleEnum) else RoleEnum(self.user.role.value)
        except Exception:
            # Fallback: assume role is Enum already
            role_enum = self.user.role

        updated = self.actuator_service.toggle_actuator(
            actuator_id=actuator_id,
            user_id=self.user.id,
            user_community=self.user.community_id,
            user_role=role_enum,
        )

        if not updated:
            # No permission or actuator not found
            self.controller._notify("No tienes permisos para cambiar este actuador.")
        else:
            self.controller._notify("Estado del actuador actualizado.")
        # We could refresh the view, but for now we don't reload the entire list.

    # -------------------------------------------------------
    # Body layout: 60/40 (B) — sensors left, actuators right
    # -------------------------------------------------------

    def build_body(self) -> ft.Control:
        # Load data for the selected community
        sensors = self.sensor_service.get_sensors_in_community(self.community_id)
        actuators = self.actuator_service.get_actuators_in_community(self.community_id)

        sensor_tiles = [self._sensor_tile(s) for s in sensors]
        if not sensor_tiles:
            sensor_tiles = [
                ft.Text("No hay sensores en esta comunidad.", size=12, color=FULL_BLACK)
            ]

        sensors_column = ft.Column(
            spacing=10,
            controls=[
                ft.Text(
                    "Sensores y su información",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=PRIMARY_GREEN,
                ),
                ft.Column(
                    spacing=10,
                    scroll=ft.ScrollMode.ALWAYS,
                    controls=sensor_tiles,
                ),
            ],
        )


        actuator_tiles = [self._actuator_tile(a) for a in actuators]
        if not actuator_tiles:
            actuator_tiles = [
                ft.Text("No hay actuadores en esta comunidad.", size=12, color=FULL_BLACK)
            ]

        actuators_column = ft.Column(
            spacing=10,
            controls=[
                ft.Text(
                    "Actuadores / control remoto",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=PRIMARY_GREEN,
                ),
                ft.Column(
                    spacing=10,
                    scroll=ft.ScrollMode.ALWAYS,
                    controls=actuator_tiles,
                ),
            ],
        )



        # Layout B: about 60/40 → expand factors 3 and 2
        return ft.Row(
            spacing=16,
            controls=[
                ft.Container(
                    alignment=ft.alignment.top_center,
                    expand=3,
                    bgcolor=BG_CARD_PRIMARY,
                    border_radius=16,
                    padding=12,
                    content=sensors_column,
                ),
                ft.Container(
                    alignment=ft.alignment.top_center,
                    expand=2,
                    bgcolor=BG_CARD_PRIMARY,
                    border_radius=16,
                    padding=12,
                    content=actuators_column,
                ),
            ],
        )
