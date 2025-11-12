import flet as ft

def basic_user_view(page: ft.Page):
    page.title = "Basic User View"
    page.bgcolor = "#2E5E5B"
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 0

    # Datos simulados
    avisos = [
        {"titulo": "Vuelo programado", "hora": "10:00 - 12:30 • Cuatro Vientos"},
        {"titulo": "Aviso de mantenimiento", "hora": "13:45 • Hangar 3"},
        {"titulo": "Reunión de instructores", "hora": "17:00 • Aula 2"},
    ]

    # Barra superior
    top_bar = ft.Container(
        padding=ft.padding.all(15),
        bgcolor="white",
        content=ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.CircleAvatar(
                            foreground_image_src = "profile2.jpeg",  # imagen local assets
                            radius= 22
                        ),
                        ft.Text("User prueba", size=18, weight=ft.FontWeight.BOLD),
                    ]
                ),
                ft.IconButton(
                    icon=ft.Icons.SETTINGS,
                    icon_color="#2260FF",
                    on_click=lambda e: print("Ir a ajustes")
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    # Función para generar las tarjetas según el ancho actual
    def generar_cards(ancho):
        return ft.Column(
            controls=[
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
                        width=ancho * 0.7,
                    )
                )
                for aviso in avisos
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER
        )

    # Crear el contenedor inicial con las tarjetas
    cards_container = ft.Container(content=generar_cards(page.width))

    # Barra inferior
    page.navigation_bar = ft.NavigationBar(
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

    # Estructura principal
    layout = ft.Column(
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

    # Actualizar tamaño dinámicamente al cambiar la ventana
    def on_resize(e):
        cards_container.content = generar_cards(page.width)
        page.update()

    page.on_resize = on_resize

    page.add(layout)



# Ejecución
if __name__ == "__main__":
    ft.app(target=basic_user_view, assets_dir="assets")
