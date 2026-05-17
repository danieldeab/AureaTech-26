# app/view/lists/view_user_management.py

import flet as ft

from app.view.base.view_base_list import BaseListView
from app.view.theme import PRIMARY_GREEN, WHITE, FULL_BLACK

from app.repository.user_repository import UserRepository
from app.model.enums import RoleEnum


class UserManagementView(BaseListView):
    """
    User management screen for ADMIN.
    Allows:
    - Filtering by role
    - Editing role and community
    - Deleting a user
    """

    def __init__(
        self,
        page: ft.Page,
        controller,
        user,
        role: str,
        on_dashboard,
        on_alerts,
        on_logout,
        on_settings,
    ):
        self.user_repo = UserRepository()
        self.selected_filter = "ALL"  # ALL, NEIGHBOR, TECHNICIAN, ADMIN
        self.show_plate_reviews = False

        # List container that we will update in-place
        self._list_view = ft.Column(
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
            height=360,
            controls=[],
        )

        super().__init__(
            page=page,
            controller=controller,
            user=user,
            role=role,
            on_dashboard=on_dashboard,
            on_alerts=on_alerts,
            on_logout=on_logout,
            on_settings=on_settings,
            title="Gestión de usuarios",
        )        

    # ===============================================================
    # INTERNAL HELPERS
    # ===============================================================
    def _get_filtered_users(self):
        users = self.user_repo.get_all()
        if self.selected_filter != "ALL":
            users = [u for u in users if u.role.value == self.selected_filter]
        return users

    def _build_tiles(self):
        users = self._get_filtered_users()
        if not users:
            return [ft.Text("No hay usuarios.", size=12)]
        return [self._user_tile(u) for u in users]

    def _get_pending_plates(self):
        getter = getattr(self.controller, "get_pending_plate_requests_for_admin", None)
        return getter() if callable(getter) else []

    def _refresh_list(self):
        self._list_view.controls = self._build_tiles()
        # Only this control changed; no need to rebuild the whole view
        if self._list_view.page:
            self._list_view.update()

    # ===============================================================
    # FILTER BAR
    # ===============================================================
    def _filter_chips(self):
        def set_filter(role_value: str):
            self.selected_filter = role_value
            self._refresh_list()

            # Update chip selected states
            for c in chips.controls:
                c.selected = (c.data == role_value)
            self.update()

        chips = ft.Row(
            spacing=12,
            controls=[
                ft.Chip(
                    label=ft.Text("Todos"),
                    selected=self.selected_filter == "ALL",
                    data="ALL",
                    on_select=lambda e: set_filter(e.control.data),
                ),
                ft.Chip(
                    label=ft.Text("Vecinos"),
                    selected=self.selected_filter == "NEIGHBOR",
                    data="NEIGHBOR",
                    on_select=lambda e: set_filter(e.control.data),
                ),
                ft.Chip(
                    label=ft.Text("Técnicos"),
                    selected=self.selected_filter == "TECHNICIAN",
                    data="TECHNICIAN",
                    on_select=lambda e: set_filter(e.control.data),
                ),
                ft.Chip(
                    label=ft.Text("Admins"),
                    selected=self.selected_filter == "ADMIN",
                    data="ADMIN",
                    on_select=lambda e: set_filter(e.control.data),
                ),
            ],
        )

        return chips

    def _plate_review_notification(self) -> ft.Control:
        pending = self._get_pending_plates()
        label = f"Solicitudes de matricula pendientes: {len(pending)}"
        return ft.Container(
            bgcolor=WHITE,
            border_radius=12,
            padding=12,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(label, color=PRIMARY_GREEN, weight=ft.FontWeight.BOLD),
                            ft.ElevatedButton(text="Revisar", on_click=self._open_plate_review_dialog),
                        ],
                    ),
                ],
            ),
        )

    def _plate_review_rows(self, pending: list[dict]) -> list[ft.Control]:
        if not pending:
            return [ft.Text("No hay matriculas pendientes.", size=12, color=FULL_BLACK)]
        rows = []
        for plate in pending:
            plate_id = plate.get("allowed_plate_id")
            rows.append(
                ft.Row(
                    spacing=12,
                    controls=[
                        ft.Container(width=120, content=ft.Text(str(plate.get("plate", "--")), color=PRIMARY_GREEN, weight=ft.FontWeight.BOLD)),
                        ft.Container(width=100, content=ft.Text(f"User {plate.get('user_id', '--')}", size=12, color=FULL_BLACK)),
                        ft.Container(width=120, content=ft.Text(f"Community {plate.get('community_id', '--')}", size=12, color=FULL_BLACK)),
                        ft.TextButton(text="Aprobar", on_click=lambda e, pid=plate_id: self._approve_plate(pid)),
                        ft.TextButton(text="Denegar", on_click=lambda e, pid=plate_id: self._deny_plate(pid)),
                    ],
                )
            )
        return rows

    # ===============================================================
    # ITEM TILE
    # ===============================================================
    def _user_tile(self, u):
        """
        Single user row:
        Name | Email | Role | Community | Delete
        """
        role_text = u.role.value if isinstance(u.role, RoleEnum) else str(u.role)
        comm = self.user_repo.get_all_communities()
        comm = [c for c in comm if c != 0]  # remove community 0

        # Dropdown for role change
        role_dropdown = ft.Dropdown(
            width=160,
            value=role_text,
            color=PRIMARY_GREEN,
            options=[ft.dropdown.Option(r.value) for r in RoleEnum],
            on_change=lambda e: self._update_role(u.id, e.control.value),
        )

        # Numeric community field
        comm_field = ft.Dropdown(
            value=str(u.community_id),
            width=80,
            color=PRIMARY_GREEN,
            focused_color=WHITE,
            options=[ft.dropdown.Option(str(c)) for c in comm],
            on_change=lambda e: self._update_community(u.id, e.control.value),
        )

        delete_btn = ft.IconButton(
            icon=ft.icons.DELETE,
            icon_color="red",
            on_click=lambda e: self._delete_user(u.id),
        )

        NAME_W = 260
        EMAIL_W = 260
        ROLE_W = 180
        COMM_W = 80

        return ft.Container(
            bgcolor=WHITE,
            padding=12,
            border_radius=12,
            content=ft.Row(
                alignment
                =ft.MainAxisAlignment.START,
                spacing=20,
                controls=[
                    ft.Container(
                        width=NAME_W,
                        content=ft.Text(
                            u.name,
                            weight=ft.FontWeight.BOLD,
                            color=PRIMARY_GREEN,
                        ),
                    ),
                    ft.Container(
                        width=EMAIL_W,
                        content=ft.Text(u.email, size=12, color=FULL_BLACK),
                    ),
                    ft.Container(width=ROLE_W, content=role_dropdown),
                    ft.Container(width=COMM_W, content=comm_field),
                    delete_btn,
                ],
            ),
        )

    # ===============================================================
    # ACTIONS
    # ===============================================================
    def _update_role(self, user_id, new_role):
        self.user_repo.update_role(user_id, new_role)
        self.controller._notify("Rol actualizado.")
        self._refresh_list()

    def _update_community(self, user_id, value):
        try:
            cid = int(value)
        except ValueError:
            self.controller._notify("ID de comunidad inválido.")
            return
        self.user_repo.update_community(user_id, cid)
        self.controller._notify("Comunidad actualizada.")
        self._refresh_list()

    def _delete_user(self, user_id):
        self.user_repo.delete_user(user_id)
        self.controller._notify("Usuario eliminado.")
        self._refresh_list()

    def _open_plate_review_dialog(self, e):
        pending = self._get_pending_plates()
        content = ft.Column(
            width=620,
            height=360,
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
            controls=self._plate_review_rows(pending),
        )
        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Solicitudes de matricula pendientes"),
            content=content,
            actions=[ft.TextButton("Cerrar", on_click=self._close_plate_review_dialog)],
        )
        self.page.dialog.open = True
        self.page.update()

    def _close_plate_review_dialog(self, e=None):
        if self.page.dialog:
            self.page.dialog.open = False
        self.page.update()

    def _approve_plate(self, allowed_plate_id):
        if allowed_plate_id is None:
            return
        ok, msg = self.controller.approve_plate_registration(int(allowed_plate_id))
        self.controller._notify(msg)
        if ok:
            self._close_plate_review_dialog()
            self.controller.show_user_management()

    def _deny_plate(self, allowed_plate_id):
        if allowed_plate_id is None:
            return
        ok, msg = self.controller.deny_plate_registration(int(allowed_plate_id))
        self.controller._notify(msg)
        if ok:
            self._close_plate_review_dialog()
            self.controller.show_user_management()

    # OVERRIDES
    def build(self):
        self._refresh_list()
        return super().build()


    # ===============================================================
    # MAIN LIST
    # ===============================================================
    def build_list(self):
        
        ''' Returns the list widget:
        [ filter bar ]
        [ scrollable list column ]'''

        return ft.Column(
            spacing=16,
            controls=[
                self._plate_review_notification(),
                self._filter_chips(),
                self._list_view,
            ],
        )
