# app/views/login.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import flet as ft
from app.models.models import Session
from app.models.auth import UserRepository, AuthController
from app.controllers.ui_controller import UIController

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Assets"))

def main(page: ft.Page):
    page.title = "AureaTech - Login"
    page.bgcolor = "#2E2E2E"
    page.padding = 16
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_min_width = 900
    page.window_min_height = 650
    page.assets_dir = ASSETS_DIR

    # Modelos / lógica de autenticación
    session = Session()
    auth = AuthController(UserRepository(), session)

    # Controlador de UI
    ui = UIController(page, auth, session, ASSETS_DIR)
    ui.show_menu()

if __name__ == "__main__":
    ft.app(target=main)
