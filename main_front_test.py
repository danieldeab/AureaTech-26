import flet as ft
from app.views.modify_user import ModifyUserView

def main(page: ft.Page):
    page.title = "AureaTech — Modify User Data"
    page.add(ModifyUserView(page, role="admin"))

ft.app(target=main)
