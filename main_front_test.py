# main_front_test.py
#
# This is a front-end entrypoint for testing the refactored auth views
# using the real UIController + real AuthController + real repository.
#

import flet as ft

from app.controller.auth_controller import AuthController
from app.repository.user_repository import UserRepository
from app.repository.log_repository import LogRepository
from app.model.models import Session
from app.controller.ui_controller import UIController


def main(page: ft.Page):
    page.title = "AureaTech – Front Test"
    page.window_width = 1100
    page.window_height = 750
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Asset directory for images
    page.assets_dir = "app/assets"

    # ----------------------------------------------
    # REAL BACKEND LAYERS
    # ----------------------------------------------
    session = Session()
    repo = UserRepository()         # loads usuarios.json
    logs = LogRepository()          # loads logs.json
    auth = AuthController(repo, session, logs)

    # ----------------------------------------------
    # UI CONTROLLER (FINAL)
    # ----------------------------------------------
    ui = UIController(page, auth, session)

    # ----------------------------------------------
    # START THE APP
    # ----------------------------------------------
    ui.show_menu()


if __name__ == "__main__":
    ft.app(target=main)
