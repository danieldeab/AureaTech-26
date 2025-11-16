import flet as ft

class BaseUserView:
    def __init__(self, page: ft.Page):
        self.page = page
        
        # Datos simulados
        self.avisos = [
            {"titulo": "Vuelo programado", "hora": "10:00 - 12:30 • Cuatro Vientos"},
            {"titulo": "Aviso de mantenimiento", "hora": "13:45 • Hangar 3"},
            {"titulo": "Reunión de instructores", "hora": "17:00 • Aula 2"},
        ]

    def build_bottom_bar(self):
        """Cada rol puede sobreescribir esto."""
        return ft.NavigationBar(
            bgcolor="white",
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icons.INFO_OUTLINE,
                    selected_icon=ft.Icons.INFO,
                    label="Histórico",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.LOGOUT,
                    selected_icon=ft.Icons.LOGOUT,
                    label="Salir",
                ),
            ],
        )

    def build_cards(self, width):
        """Se puede sobreescribir para que cada rol tenga otras tarjetas."""
        return [
            ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(aviso["titulo"], weight=ft.FontWeight.BOLD),
                            ft.Text(aviso["hora"], size=15, color="grey"),
                        ]
                    ),
                    padding=15,
                    bgcolor="white",
                    border_radius=12,
                    width=width * 0.7,
                )
            )
            for aviso in self.avisos
        ]

    def build(self):
        self.page.title = "Basic User View"
        self.page.bgcolor = "#2E5E5B"
        self.page.padding = 0
        self.page.scroll = ft.ScrollMode.AUTO

        # TOP BAR
        top_bar = ft.Container(
            padding=15,
            bgcolor="white",
            content=ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            ft.CircleAvatar(
                                foreground_image_src="profile2.jpeg",
                                radius=22,
                            ),
                            ft.Text("User prueba", size=18, weight=ft.FontWeight.BOLD),
                        ]
                    ),
                    ft.IconButton(
                        icon=ft.Icons.SETTINGS,
                        icon_color="#2260FF",
                        on_click=lambda e: print("Ir a ajustes"),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        # CARDS
        cards_column = ft.Column(
            controls=self.build_cards(self.page.width),
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        cards_container = ft.Container(content=cards_column)

        self.page.navigation_bar = self.build_bottom_bar()

        def on_resize(e):
            cards_column.controls = self.build_cards(self.page.width)
            cards_column.update()

        self.page.on_resize = on_resize

        main_view = ft.Column(
            expand=True,
            controls=[
                top_bar,
                ft.Container(
                    expand=True,
                    alignment=ft.alignment.center,
                    content=cards_container,
                ),
            ],
        )
        
        return main_view

def main(page: ft.Page):
    view = BaseUserView(page)
    page.add(view.build())

ft.app(target=main)
