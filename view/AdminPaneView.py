import flet as ft
from view.BasePaneView import BaseUserView

class AdminPaneView(BaseUserView):
    def __init__(self, page: ft.Page):
        super().__init__(page)

    def build_bottom_bar(self):
        base_bar = super().build_bottom_bar()

        admin_destinations = [
            ft.NavigationBarDestination(
                icon=ft.Icons.MEMORY_OUTLINED,
                selected_icon=ft.Icons.MEMORY,
                label="Actuadores"
            ),
            ft.NavigationBarDestination(
                icon = ft.Icons.STORAGE_OUTLINED,
                selected_icon=ft.Icons.STORAGE,
                label="Historial"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.PEOPLE_OUTLINED,
                selected_icon=ft.Icons.PEOPLE,
                label="Gestión de usuarios"
            )

        ]

        base_bar.destinations = admin_destinations + base_bar.destinations

        return base_bar

# main de prueba para previsualizar

def main(page: ft.Page):
    view = AdminPaneView(page)   # usar la clase hija
    page.add(view.build())

ft.app(target=main)