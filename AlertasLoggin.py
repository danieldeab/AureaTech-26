import flet as ft  
# Importamos la librería Flet (versión 0.28.x)
# Para ejecutar este script:
# 1. Crear un entorno virtual (si no lo tienes):
# .\venv\Scripts\Activate.ps1


# ==============================
# 🎨 Paleta de colores personalizada
# Basada en el mockup de AureaTech
# ==============================
PRIMARY_GREEN = "#2D4A46"   # Verde principal (botones / branding)
LIGHT_LILAC   = "#DCE0FF"   # Lila claro usado en botones del login
LIGHT_GREEN   = "#1EF0A0"   # Verde pastel (alerta de éxito)
ERROR_RED     = "#C62828"   # Rojo para errores
WARNING_YELL  = "#FFEB99"   # Amarillo para advertencias
INFO_BLUE     = "#CFE2FF"   # Azul para información
WHITE         = "#FFFFFF"   # Blanco (texto o fondo)

# ==============================
# 🔸 Función auxiliar: icono genérico
# (como Flet 0.28 no tiene ft.icons, 
#  hacemos un círculo con un "!" dentro)
# ==============================
def bullet_icon(bg, fg):
    """
    Crea un ícono circular de color `fg`
    con un signo de exclamación dentro (color `bg`).
    """
    return ft.Stack(
        controls=[
            # Círculo de fondo
            ft.Container(width=22, height=22, bgcolor=fg, border_radius=11),
            # Signo "!" centrado
            ft.Container(
                width=22, height=22,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("!", color=bg, size=14, weight=ft.FontWeight.BOLD)
                    ],
                ),
            ),
        ]
    )

# ==============================
# 🔹 Función para crear una alerta genérica
# ==============================
def AlertBox(message, bg, fg, dense=False):
    """
    Crea una alerta visual con:
    - `message`: texto de la alerta
    - `bg`: color de fondo (hex)
    - `fg`: color del texto e icono
    - `dense`: versión más compacta (True/False)
    """
    return ft.Container(
        bgcolor=bg,  # color de fondo de la alerta
        border_radius=20,  # bordes redondeados
        padding=ft.padding.symmetric(
            14 if not dense else 8,  # alto
            12 if not dense else 8   # ancho
        ),
        content=ft.Row(
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                bullet_icon(bg, fg),  # “icono” circular de exclamación
                ft.Text(
                    message,
                    color=fg,
                    size=16 if not dense else 14
                ),
            ],
        ),
    )

# ==============================
# 🖼️ Función principal de la app (solo las alertas)
# ==============================
def main(page: ft.Page):
    # Configuración básica de la ventana
    page.title = "Diseño de Alertas - AureaTech"
    page.bgcolor = WHITE
    page.padding = 40
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # 🔴 Alerta de ERROR
    alert_error = AlertBox(
        "Error: Credenciales incorrectas.",
        ERROR_RED,
        WHITE
    )

    # 🟡 Alerta de ADVERTENCIA
    alert_warning = AlertBox(
        "Advertencia: Hay campos vacíos.",
        WARNING_YELL,
        PRIMARY_GREEN
    )

    # 🔵 Alerta de INFORMACIÓN
    alert_info = AlertBox(
        "Info: La contraseña requiere 6+ caracteres.",
        INFO_BLUE,
        PRIMARY_GREEN
    )

    # 🟢 Alerta de ÉXITO
    alert_success = AlertBox(
        "Inicio de sesión correcto.",
        LIGHT_GREEN,
        PRIMARY_GREEN
    )

    # Agregamos las alertas a la página
    page.add(
        ft.Column(
            spacing=25,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "Ejemplos de alertas visuales",
                    color=PRIMARY_GREEN,
                    size=20,
                    weight=ft.FontWeight.BOLD
                ),
                alert_error,
                alert_warning,
                alert_info,
                alert_success,
            ],
        )
    )

# Ejecutar la aplicación
ft.app(target=main)

# 1. Crear un entorno virtual (si no lo tienes):
# .\venv\Scripts\Activate.ps1