import flet as ft


class ModifyUserView(ft.UserControl):
    """
    Wireframe view for modifying user data.
    Common base view for Admin, Technician, and Neighbor roles.
    Future role-specific views may subclass this one.
    """

    def __init__(self, page: ft.Page, role: str = "user", user_data: dict | None = None):
        super().__init__()
        self.page = page
        self.role = role
        self.user_data = user_data or {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "password": "********",
            "role": "Neighbor",
            "sensors": ["DHT22", "LDR", "HC-SR04"]
        }

        # Common text fields
        self.name_field = ft.TextField(label="Full Name", value=self.user_data["name"], width=300)
        
        self.email_field = ft.TextField(label="Email", value=self.user_data["email"], width=300)
        self.confirm_email_field = ft.TextField(label="Confirm Email", value=self.user_data["email"], width=300)
        
        self.password_field = ft.TextField(
            label="Password"
            , value=self.user_data["password"]
            , password=True
            , can_reveal_password=True
            , width=300
        )
        self.confirm_password_field = ft.TextField(
            label="Confirm Password"
            , value=self.user_data["password"]
            , password=True
            , can_reveal_password=True
            , width=300
        )

        # Role-specific or optional fields
        self.role_dropdown = ft.Dropdown(
            label="Role",
            options=[
                ft.dropdown.Option("Admin"),
                ft.dropdown.Option("Technician"),
                ft.dropdown.Option("Neighbor")
            ],
            width=300,
            visible=(self.role == "admin")  # only visible for admins
        )

        self.sensors_field = ft.TextField(
            label="Assigned Sensors (comma separated)"
            , value=", ".join(self.user_data["sensors"])
            , width=300
            , visible=(self.role in ["admin", "technician"])
        )

        # Buttons
        self.save_button = ft.ElevatedButton("Save Changes", on_click=self.save_changes)
        self.cancel_button = ft.OutlinedButton("Back", on_click=self.go_back)

    def build(self):
        # Header section (placeholder logo area)
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Image(src="/app/assets/logo.png", width=50, height=50),
                    ft.Text("AureaTech — Modify User Data", size=20, weight=ft.FontWeight.BOLD),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.padding.all(20),
        )

        # Form body
        form = ft.Column(
            controls=[
                self.name_field,
                self.email_field,
                self.confirm_email_field,
                self.password_field,
                self.confirm_password_field,
                self.role_dropdown,
                self.sensors_field,
                ft.Row(
                    controls=[self.save_button, self.cancel_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        )

        # Footer placeholder
        footer = ft.Container(
            content=ft.Text("© AureaTech 2025 — Wireframe UI", size=12, italic=True),
            alignment=ft.alignment.center,
            padding=ft.padding.symmetric(vertical=10),
        )

        layout = ft.Column(
            controls=[header, ft.Divider(), form, ft.Divider(), footer],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        )

        return layout

    # --- Placeholder event handlers ---
    def save_changes(self, e):
        # Simple placeholder logic
        if self.email_field.value != self.confirm_email_field.value:
            msg = "Email and confirmation do not match."
        elif self.password_field.value != self.confirm_password_field.value:
            msg = "Password and confirmation do not match."
        else:
            msg = "Changes saved successfully (simulation)."
        
        self.page.snack_bar = ft.SnackBar(ft.Text(msg))
        self.page.snack_bar.open = True
        self.page.update()

    def go_back(self, e):
        # Placeholder redirect (later integrated with your routing controller)
        self.page.go("/views")
