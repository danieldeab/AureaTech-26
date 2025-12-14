import flet as ft
from datetime import date, datetime

from app.view.theme import (
    PRIMARY_GREEN,
    LIGHT_GREY,
    WHITE,
    BACK_BLUE,
    FULL_BLACK,
    TEXT_SECONDARY,
    BRAND_ACCENT_BLUE,
    INPUT_PLACEHOLDER,
    INPUT_TEXT,
)
from app.view.base.view_base_auth import ViewBaseAuth


class SignupView(ViewBaseAuth):
    """
    Sign Up screen.

    Controller must expose:
      - controller.signup(fullname, email, community_id, password, dob, picture_path=None)
      - controller.go_back()
      - controller.go_login()
    """

    def __init__(self, page: ft.Page, controller, on_back_click=None):
        super().__init__(
            page=page,
            controller=controller,
            title="New Account",
            subtitle="",
            show_back=True,
        )

        self.on_back_click = on_back_click or controller.go_back

        self.fullname_field = None
        self.community_id_field = None
        self.password_field = None
        self.email_field = None
        self.dob_display = None

        self.profile_picture_path = None
        self.profile_preview = None

        # --------------------------
        # Calendar DatePicker
        # --------------------------
        self.date_picker = ft.DatePicker(
            first_date=date(1900, 1, 1),
            last_date=date.today(),
            on_change=self._on_date_selected,
        )
        self.page.overlay.append(self.date_picker)

        # --------------------------
        # File Picker for profile picture
        # --------------------------
        self.file_picker = ft.FilePicker(on_result=self._on_file_picked)
        self.page.overlay.append(self.file_picker)

    # Override to keep per-view back handler
    def _make_back_button(self):
        back_icon = ft.Image(
            src=f"{self.page.assets_dir}/back.png",
            width=26,
            height=26,
            error_content=ft.Text("<", color=BACK_BLUE,
                                  size=26, weight=ft.FontWeight.BOLD),
        )
        return ft.GestureDetector(
            on_tap=lambda e: (
                self.on_back_click(),
            ),
            content=ft.Container(padding=6, content=back_icon),
        )

    # --------------------------
    # DATE PICKER CALLBACK
    # --------------------------
    def _on_date_selected(self, e):
        if e.control.value:
            selected = e.control.value
            formatted = selected.strftime("%d / %m / %Y")
            self.dob_display.value = formatted
            self.dob_display.update()

    # --------------------------
    # FILE PICKER CALLBACK
    # --------------------------
    def _on_file_picked(self, e: ft.FilePickerResultEvent):
        if e.files:
            file = e.files[0]
            self.profile_picture_path = file.path
            self.profile_preview.src = file.path
            self.profile_preview.update()

   
    # --------------------------
    # DROPDOWN METHOD
    # --------------------------
    def _open_dropdown(self, e):
        self.community_id_field.open = True
        self.update()   # optional, but often needed in Flet


    # --------------------------
    # ERROR SNACKBAR HELPER
    # --------------------------
    def _error(self, msg):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg))
        self.page.snack_bar.open = True
        self.page.update()

    # --------------------------
    # MAIN BODY
    # --------------------------
    def build_body(self) -> ft.Control:
        FIELD_W = 460
        FONT_SIZE_LABEL = 14
        FIELD_SPACE = 10

        # -----------------------------------------------------
        # FIELDS
        # -----------------------------------------------------
        self.fullname_field = ft.TextField(
            label="Nombre completo",
            label_style=ft.TextStyle(color=PRIMARY_GREEN),
            hint_text="Nombre completo",
            width=FIELD_W,
            bgcolor=LIGHT_GREY,
            border_radius=12,
            border=ft.InputBorder.NONE,
            color=INPUT_TEXT,
            hint_style=ft.TextStyle(color=INPUT_PLACEHOLDER),
            content_padding=ft.padding.symmetric(12, 14),
            on_submit=lambda e: self.community_id_field.focus(),
        )

        self.community_id_field = ft.Dropdown(
            label="Community ID",
            label_style=ft.TextStyle(color=PRIMARY_GREEN),
            width=FIELD_W,
            bgcolor=LIGHT_GREY,
            border_radius=12,
            border=ft.InputBorder.NONE,
            color=INPUT_TEXT,
            hint_style=ft.TextStyle(color=INPUT_PLACEHOLDER),
            content_padding=ft.padding.symmetric(12, 14),
            options=[
                ft.dropdown.Option("1"),
                ft.dropdown.Option("2"),
            ],
            focused_bgcolor=WHITE,
            focused_border_color=PRIMARY_GREEN,
            focused_border_width=2,
            focused_color=FULL_BLACK,
            on_change=lambda e: self.password_field.focus(),
            on_focus=self._open_dropdown,
        )

        self.password_field = ft.TextField(
            label="Contraseña",
            label_style=ft.TextStyle(color=PRIMARY_GREEN),
            hint_text="Contraseña",
            password=True,
            can_reveal_password=True,
            width=FIELD_W,
            bgcolor=LIGHT_GREY,
            border_radius=12,
            border=ft.InputBorder.NONE,
            color=INPUT_TEXT,
            hint_style=ft.TextStyle(color=INPUT_PLACEHOLDER),
            content_padding=ft.padding.symmetric(12, 14),
            on_submit=lambda e: self.email_field.focus(),
        )

        self.email_field = ft.TextField(
            label="Email",
            label_style=ft.TextStyle(color=PRIMARY_GREEN),
            hint_text="example@example.com",
            width=FIELD_W,
            bgcolor=LIGHT_GREY,
            border_radius=12,
            border=ft.InputBorder.NONE,
            color=INPUT_TEXT,
            hint_style=ft.TextStyle(color=INPUT_PLACEHOLDER),
            content_padding=ft.padding.symmetric(12, 14),
            on_submit=lambda e: self.date_picker.pick_date(),
        )

        # --------------------------
        # READ-ONLY DOB DISPLAY
        # --------------------------
        self.dob_display = ft.TextField(
            label="Fecha de nacimiento",
            label_style=ft.TextStyle(color=PRIMARY_GREEN),
            read_only=True,
            hint_text="Select a date",
            width=FIELD_W,
            bgcolor=LIGHT_GREY,
            border_radius=12,
            border=ft.InputBorder.NONE,
            color=INPUT_TEXT,
            hint_style=ft.TextStyle(color=INPUT_PLACEHOLDER),
            content_padding=ft.padding.symmetric(12, 14),
            suffix=ft.IconButton(
                icon=ft.icons.CALENDAR_MONTH,
                icon_size=20,
                icon_color=PRIMARY_GREEN,
                on_click=lambda e: self.date_picker.pick_date(),
            ),
        )

        # -----------------------------------------------------
        # PROFILE PICTURE UPLOAD
        # -----------------------------------------------------
        self.profile_preview = ft.Image(
            src="",
            width=80,
            height=80,
            border_radius=40,
            fit=ft.ImageFit.COVER,
        )

        upload_picture_button = ft.ElevatedButton(
            "Upload Profile Picture (optional)",
            on_click=lambda e: self.file_picker.pick_files(
                allow_multiple=False,
                file_type=ft.FilePickerFileType.IMAGE,
            ),
            bgcolor=PRIMARY_GREEN,
            color=WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=20)
            ),
        )

        # -----------------------------------------------------
        # SUBMIT HANDLER
        # -----------------------------------------------------
        def _submit(e=None):
            # Validate DOB
            if not self.dob_display.value:
                self._error("Por favor seleccione su fecha de nacimiento.")
                return

            raw = self.dob_display.value.replace(" ", "").replace("/", "")
            try:
                d = datetime.strptime(raw, "%d%m%Y").date()
            except ValueError:
                self._error("La fecha seleccionada no es válida.")
                return

            if d > date.today():
                self._error("La fecha no puede ser futura.")
                return

            # Controller call
            self.controller.signup(
                self.fullname_field.value,
                self.community_id_field.value,
                self.email_field.value,
                self.password_field.value,
                d.strftime("%d/%m/%Y"),
                picture_path=self.profile_picture_path,
            )

        signup_cta = ft.ElevatedButton(
            "Sign Up",
            width=260,
            height=48,
            bgcolor=PRIMARY_GREEN,
            color=WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=24)
            ),
            on_click=_submit,
        )

        terms = ft.Text(
            "By continuing, you agree to Terms of Use and Privacy Policy.",
            size=11,
            color=BACK_BLUE,
            text_align=ft.TextAlign.CENTER,
        )

        footer_row = ft.Row(
            controls=[
                ft.Text("Already have an account? ", color=TEXT_SECONDARY),
                ft.TextButton(
                    "Log in",
                    style=ft.ButtonStyle(color=BRAND_ACCENT_BLUE),
                    on_click=lambda e: self.controller.go_login(),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        # -----------------------------------------------------
        # FINAL LAYOUT
        # -----------------------------------------------------
        return ft.Column(
            controls=[
                ft.Text("Nombre completo", color=PRIMARY_GREEN, size=FONT_SIZE_LABEL),
                self.fullname_field,
                ft.Container(height=FIELD_SPACE),

                ft.Text("Community ID", color=PRIMARY_GREEN, size=FONT_SIZE_LABEL),
                self.community_id_field,
                ft.Container(height=FIELD_SPACE),

                ft.Text("Contraseña", color=PRIMARY_GREEN, size=FONT_SIZE_LABEL),
                self.password_field,
                ft.Container(height=FIELD_SPACE),

                ft.Text("Email", color=PRIMARY_GREEN, size=FONT_SIZE_LABEL),
                self.email_field,
                ft.Container(height=FIELD_SPACE),

                ft.Text("Fecha de nacimiento", color=PRIMARY_GREEN, size=FONT_SIZE_LABEL),
                self.dob_display,
                ft.Container(height=FIELD_SPACE),

                ft.Text("Foto de perfil (opcional)", color=PRIMARY_GREEN, size=FONT_SIZE_LABEL),
                self.profile_preview,
                upload_picture_button,
                ft.Container(height=14),

                terms,
                ft.Container(height=14),

                signup_cta,
                ft.Container(height=6),

                footer_row,
            ],
            spacing=6,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

