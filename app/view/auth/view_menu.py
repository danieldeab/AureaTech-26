# app/view/auth/view_menu.py

import os
import flet as ft
from app.view.theme import (
    PRIMARY_GREEN, LIGHT_GREY, WHITE, BACK_BLUE,
    BORDER_SOFT, PANEL_W, PANEL_H
)

class MenuView( ft.UserControl):
    """
    Main entry menu where the user chooses:
        - Login
        - Sign Up

    Controller must expose:
        - controller.go_login()
        - controller.go_signup()
    """

    def __init__(self, page: ft.Page, controller):
        super().__init__()
        self.page = page
        self.controller = controller

 

    def build(self):
        bottom_h = int(PANEL_H * 0.18)

        # ---------------------------------------------------
        # Logo
        # ---------------------------------------------------
        logo = ft.Image(
            src=os.path.join(self.page.assets_dir, "logo.png"),
            width=220,
            height=220,
            fit=ft.ImageFit.CONTAIN,
            error_content=ft.Text("No se encontró 'logo.png'", color="red"),
        )
        # ---------------------------------------------------
        # Buttons
        # ---------------------------------------------------
        btn_login = ft.ElevatedButton(
            "Login",
            width=300,
            height=52,
            bgcolor=LIGHT_GREY,
            color=PRIMARY_GREEN,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=26)),
            on_click=lambda e: self.controller.go_login(),
        )

        btn_signup = ft.ElevatedButton(
            "Sign Up",
            width=300,
            height=52,
            bgcolor=PRIMARY_GREEN,
            color=WHITE,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=26)),
            on_click=lambda e: self.controller.go_signup(),
        )

        # ---------------------------------------------------
        # Center content
        # ---------------------------------------------------
        content = ft.Container(
            alignment=ft.alignment.center,
            expand=True,
            content=ft.Column(
                controls=[logo, btn_login, btn_signup],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
        )

        # ---------------------------------------------------
        # Final wrapped container
        # ---------------------------------------------------
        return ft.Container(
            width=PANEL_W,
            height=PANEL_H,
            bgcolor=WHITE,
            border_radius=22,
            border=ft.border.all(1, BORDER_SOFT),
            content=ft.Stack(
                controls=[
                    # Sun image (top-left)
                    ft.Container(
                        content=ft.Image(
                            src=os.path.join(self.page.assets_dir, "sol.png"),
                            
                            width=140,
                            fit=ft.ImageFit.CONTAIN,
                            error_content=ft.Text("No se encontró 'sol.png'", color="red"),
                        ),
                        left=8,
                        top=8,
                    ),

                    # Bottom stripe image
                    ft.Container(
                        bottom=0,
                        left=0,
                        right=0,
                        content=ft.Image(
                            src=os.path.join(self.page.assets_dir, "parte_inferior.png"),
                            width=PANEL_W,
                            height=bottom_h,
                            fit=ft.ImageFit.COVER,
                            error_content=ft.Text("No se encontró 'parte_inferior.png'", color="red"),
                        ),
                    ),
                    # Main content
                    content,
                ]
            ),
        )
