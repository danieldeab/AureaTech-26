import flet as ft

def main(page: ft.Page):
    page.title = "Login / Registro - Minimal"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = "#f4f4f4"

    # ---------- FUNCIONES ----------
    def mostrar_login(e=None):
        contenedor.controls.clear()
        contenedor.controls.append(login_view)
        page.update()

    def mostrar_registro(e=None):
        contenedor.controls.clear()
        contenedor.controls.append(register_view)
        page.update()

    def login_click(e):
        user = correo_input.value
        password = pass_input.value
        page.snack_bar = ft.SnackBar(ft.Text(f"Intentando login como: {user}"))
        page.snack_bar.open = True
        page.update()

    def registrar_click(e):
        user = reg_user.value
        email = reg_email.value
        password = reg_pass.value
        page.snack_bar = ft.SnackBar(ft.Text(f"Registrando usuario: {user}"))
        page.snack_bar.open = True
        page.update()

    # ---------- LOGIN ----------
    correo_input = ft.TextField(label="Correo Electronico", width=250)
    pass_input = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=250)
    login_btn = ft.ElevatedButton("Iniciar sesión", on_click=login_click, width=250)
    switch_to_register = ft.TextButton("¿No tienes cuenta? Regístrate", on_click=mostrar_registro)

    login_view = ft.Column(
        [
            ft.Text("Iniciar Sesión", size=25, weight=ft.FontWeight.BOLD),
            correo_input,
            pass_input,
            login_btn,
            switch_to_register
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # ---------- REGISTRO ----------
    reg_user = ft.TextField(label="Usuario", width=250)
    reg_email = ft.TextField(label="Correo electrónico", width=250)
    reg_pass = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=250)
    reg_btn = ft.ElevatedButton("Crear cuenta", on_click=registrar_click, width=250)
    switch_to_login = ft.TextButton("¿Ya tienes cuenta? Inicia sesión", on_click=mostrar_login)

    register_view = ft.Column(
        [
            ft.Text("Crear Cuenta", size=25, weight=ft.FontWeight.BOLD),
            reg_user,
            reg_email,
            reg_pass,
            reg_btn,
            switch_to_login
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # Contenedor principal (vista inicial: login)
    contenedor = ft.Column([login_view], alignment=ft.MainAxisAlignment.CENTER)
    page.add(contenedor)

# Ejecutar la app
ft.app(target=main)
