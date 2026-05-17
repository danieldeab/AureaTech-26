import traceback
import flet as ft


def _capture_startup_error(exc: Exception) -> None:
    try:
        from app.service.error_service import ErrorService

        ErrorService().capture_exception(
            exc,
            severity="ERROR",
            source_layer="STARTUP",
            target_entity_type="application",
        )
    except Exception:
        # If DB logging cannot start, keep original traceback path.
        pass


def main(page: ft.Page):
    page.title = "AureaTech - Front Test"
    page.fonts = {
        "Poppins": "https://st.1001fonts.net/download/font/poppins.regular.ttf",
    }
    page.window_width = 1100
    page.window_height = 750
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme = ft.Theme(font_family="Poppins")
    page.assets_dir = "app/assets"

    try:
        from app.controller.auth_controller import AuthController
        from app.repository.user_repository import UserRepository
        from app.repository.log_repository import LogRepository
        from app.service.audit_log_service import AuditLogService
        from app.service.error_service import ErrorService
        from app.utils.session import Session
        from app.controller.ui_controller import UIController

        session = Session()
        repo = UserRepository()
        logs = LogRepository()
        audit_log_service = AuditLogService(logs)
        error_service = ErrorService()
        auth = AuthController(
            repo,
            session,
            logs,
            audit_log_service=audit_log_service,
            error_service=error_service,
        )

        ui = UIController(page, auth, session)
        ui.show_menu()
    except Exception as exc:
        _capture_startup_error(exc)
        page.clean()
        page.add(
            ft.Text("Application startup error", color=ft.colors.RED, size=18),
            ft.Text(str(exc), selectable=True),
        )
        page.update()
        print(traceback.format_exc())


if __name__ == "__main__":
    try:
        ft.app(target=main)
    except Exception as exc:
        _capture_startup_error(exc)
        raise
