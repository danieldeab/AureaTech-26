import flet as ft
from app.controller.auth_controller import AuthController
from app.controller.ui_controller import UIController
from app.repository.user_repository import UserRepository
from app.utils.session import Session

def main(page: ft.Page):
    page.title = "AureaTech"
    page.assets_dir = "app/assets"

    session = Session()
    repo = UserRepository()
    auth = AuthController(repo, session)
    ui = UIController(page, auth, session)

    ui.show_menu()

if __name__ == "__main__":
    ft.app(target=main)
