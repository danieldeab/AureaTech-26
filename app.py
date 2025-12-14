import flet as ft

from app.controller.auth_controller import AuthController
from app.repository.user_repository import UserRepository
from app.repository.log_repository import LogRepository
from app.repository.sensor_repository import SensorRepository
from app.repository.reading_repository import ReadingRepository
from app.repository.alert_repository import AlertRepository
from app.service.monitoring_service import MonitoringService
from app.utils.session import Session
from app.controller.ui_controller import UIController


def main(page: ft.Page):
    page.title = "AureaTech – Front Test"
    page.fonts = {
        "Poppins": "https://st.1001fonts.net/download/font/poppins.regular.ttf",
    }
    page.window_width = 1100
    page.window_height = 750
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme = ft.Theme(font_family="Poppins")

    # Asset directory for images
    page.assets_dir = "app/assets"

    # ----------------------------------------------
    # REAL BACKEND LAYERS
    # ----------------------------------------------
    session = Session()
    repo = UserRepository()         # loads usuarios.json
    logs = LogRepository()          # loads logs.json
    auth = AuthController(repo, session, logs)

    sensor_repo = SensorRepository()
    reading_repo = ReadingRepository()
    alert_repo = AlertRepository()

    monitoring_service = MonitoringService(
        sensor_repo,
        reading_repo,
        alert_repo,
        logs,
    )

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
