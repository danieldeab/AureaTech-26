# app/view/lists/view_alerts_dashboard.py

import flet as ft

from app.view.base.view_base_list import BaseListView
from app.view.components.alerts_view import AlertsList


class AlertsDashboardView(BaseListView):
    """
    Full-screen alerts list, reachable from the dashboard bottom nav.

    It shows:
      - Standard header (avatar, name, role)
      - Optional title "Alertas"
      - Scrollable list of alerts using AlertsList component
    """

    def __init__(
        self,
        page: ft.Page,
        controller,
        user,
        role: str,
        alerts: list,
        on_dashboard,
        on_alerts,
        on_logout,
        on_back=None,
        on_settings=None,
        on_mark_read=None,
    ):
        super().__init__(
            page=page,
            controller=controller,
            user=user,
            role=role,
            on_dashboard=on_dashboard,
            on_alerts=on_alerts,
            on_logout=on_logout,
            on_back=on_back,
            on_settings=on_settings,
            title="Alertas",
        )
        self.alerts = alerts
        self.on_mark_read = on_mark_read


    def build_list(self) -> ft.Control:
        """
        Use your existing AlertsList component to render the alerts.
        """
        return ft.Container(
            height=430,
            content=ft.ListView(
                spacing=10,
                controls=[AlertsList(alerts=self.alerts, on_mark_read=self.on_mark_read)],
            ),
        )
