""""
import flet as ft
from view.BasePaneView import BaseUserView

class AdminPaneView(BaseUserView):
    def __init__(self, page: ft.Page):
        super().__init__(page)


       #ejemplo
        self.avisos = {
            "titulo": "Panel de administración", "hora": "Acceso completo"
        }


        En esta clase se añaden las diferencias del panel de administrador heredando de la estructura base
"""