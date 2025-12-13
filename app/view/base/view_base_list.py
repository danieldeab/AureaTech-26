# app/view/base/view_base_list.py

import flet as ft
from app.view.base.view_base_dashboard import BaseDashboardView


class BaseListView(BaseDashboardView):
    
    '''Base class for list-type screens (users, sensors, actuators, alerts, ...).

    It reuses BaseDashboardView (header + bottom navigation) and introduces
    a simple convention: children implement `build_list()` instead of
    `build_body()`.'''
    
    def __init__(
        self,
        page: ft.Page,
        controller,
        user,
        role: str,
        on_dashboard,
        on_alerts,
        on_logout,
        on_back=None,
        on_settings = None,
        title: str | None = None,
    ):
        super().__init__(
            page=page,
            controller=controller,
            user=user,
            role=role,
            on_settings=on_settings or (lambda e=None: None),      
            on_dashboard=on_dashboard,     
            on_alerts=on_alerts,           
            on_logout=on_logout,           
            on_back=on_back,               
        )
        self.title = title or ""

    def build_body(self) -> ft.Control:
        '''
        Wraps the list contents with an optional title.
        Children override `build_list()` to provide the actual list control.
        '''

        controls: list[ft.Control] = []

        if self.title:
            controls.append(
                ft.Text(
                    self.title,
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=None,
                )
            )

        # Main list content provided by subclasses
        controls.append(self.build_list())

        return ft.Column(
            spacing=10,
            expand=True,
            controls=controls,
        )

    def build_list(self) -> ft.Control:
        '''    
        Must be implemented by subclasses to return the list widget.
        '''
        raise NotImplementedError("build_list() must be implemented in subclasses.")
