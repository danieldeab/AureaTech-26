import flet as ft

# Controller imports
from app.controller.auth_controller import AuthController, Session
from app.controller.dashboard_controller import DashboardController
from app.model.enums import RoleEnum

# View imports
from app.view.auth.view_login import LoginView
from app.view.auth.view_signup import SignupView
from app.view.auth.view_menu import MenuView
from app.view.auth.view_recover import RecoverPasswordView
from app.view.auth.view_reset_password import ResetPasswordView
from app.view.lists.view_alerts_dashboard import AlertsDashboardView
from app.view.lists.view_user_management import UserManagementView
from app.view.lists.view_faqs import FaqsView
from app.view.lists.view_chat_thread_list import ChatThreadListView
from app.view.chats.view_chat_messages import ChatMessagesView
from app.view.dashboard.view_user_dashboard import UserDashboardView
from app.view.dashboard.view_admin_dashboard import AdminDashboardView
from app.view.dashboard.view_tecnico_dashboard import TechnicianDashboardView
from app.view.dashboard.view_info_control import InfoControlView
from app.view.edit.view_user_edit import UserEditView
from app.view.historico.view_sya_history import HistoryView

# Repository imports
from app.repository.alert_repository import AlertRepository
from app.repository.sensor_repository import SensorRepository
from app.repository.actuator_repository import ActuatorRepository
from app.repository.log_repository import LogRepository
from app.repository.reading_repository import ReadingRepository
from app.repository.faq_repository import FAQRepository
from app.repository.chat_repository import ChatRepository
from app.repository.plate_repository import PlateRepository

# Service imports
from app.service.alert_service import AlertService
from app.service.dashboard_service import DashboardService
from app.service.monitoring_service import MonitoringService
from app.service.actuator_service import ActuatorService
from app.service.user_service import UserService
from app.service.audit_log_service import AuditLogService
from app.service.error_service import ErrorService
from app.service.chat_service import ChatService
from app.service.plate_recognition_service import PlateRecognitionService

# Theme imports
from app.view.theme import (
    SUCCESS_GREEN,
    ERROR_RED,
    PRIMARY_GREEN,
)

# Dashboard imports will be added once dashboard migration is complete
# from app.view.dashboard.main_dashboard import MainDashboardView
# from app.view.admin.admin_dashboard import AdminDashboardView
# ...


class UIController:
    """
    Final UI Controller integrating:
      - Authentication flow (Menu → Login → Signup → Recover → Reset)
      - Navigation stack for back-navigation
      - AuthController for authentication logic

    Responsibilities according to the class diagram:
      - Navigation between all views
      - Delegation of login/signup/reset to AuthController
      - Global user session and role handling
    """

    def __init__(self, page: ft.Page, auth_controller: AuthController, session: Session):
        self.page = page
        self.auth = auth_controller
       
        # Alerts
        self.alert_repo = AlertRepository()
        self.alert_service = AlertService(self.alert_repo)

        # Dashboard summary / infra
        self.sensor_repo = SensorRepository()
        self.actuator_repo = ActuatorRepository()
        self.log_repo = LogRepository()
        self.reading_repo = ReadingRepository()
        self.audit_log_service = AuditLogService(self.log_repo)
        self.error_service = ErrorService()

        self.actuator_service = ActuatorService(
            self.actuator_repo,
            audit_log_service=self.audit_log_service,
            error_service=self.error_service,
        )
        self.user_service = UserService(
            auth_controller.repo,
            audit_log_service=self.audit_log_service,
            error_service=self.error_service,
        )

        self.monitoring_service = MonitoringService(
            self.sensor_repo,
            self.reading_repo,
            self.alert_service,
            self.log_repo,
            audit_log_service=self.audit_log_service,
            error_service=self.error_service,
        )

        self.faq_repo = FAQRepository()
        self.chat_repo = ChatRepository()
        self.plate_repo = PlateRepository()
        self.chat_service = ChatService(
            chat_repository=self.chat_repo,
            user_repository=auth_controller.repo,
            faq_repository=self.faq_repo,
            audit_log_service=self.audit_log_service,
            error_service=self.error_service,
        )
        self.plate_service = PlateRecognitionService(
            self.plate_repo,
            audit_log_service=self.audit_log_service,
            error_service=self.error_service,
            alert_service=self.alert_service,
            user_repository=auth_controller.repo,
        )

        self.dashboard = DashboardController(
            self.alert_service,
            self.monitoring_service,
            session,
            self.actuator_service,
            self.log_repo,
            user_repository=auth_controller.repo,
            faq_repository=self.faq_repo,
            chat_repository=self.chat_repo,
            chat_service=self.chat_service,
        )

        self.dashboard_service = DashboardService(
            self.sensor_repo,
            self.actuator_repo,
            self.alert_service,
            self.log_repo,
            self.reading_repo,
        )
        self.session = session

        self.history = []             # navigation stack
        self.page.assets_dir = "app/assets"
        self.admin_chart_period = "7d"

    # ======================================================
    # Internal navigation utilities
    # ======================================================
    def _push(self, name: str, view: ft.Control):
        if not self.history or self.history[-1] != name:
            self.history.append(name)

        self.page.controls.clear()
        self.page.add(view)
        self.page.update()

    def _replace(self, name: str, view: ft.Control):
        if self.history:
            self.history[-1] = name
        else:
            self.history.append(name)

        self.page.controls.clear()
        self.page.add(view)
        self.page.update()

    def _notify(self, msg):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg))
        self.page.snack_bar.open = True
        self.page.update()

    # For admins to change the community of another user
    def switch_community(self, new_id):
        self.session.current_community_id = new_id
        return self.show_admin_dashboard()

    # For admins to select a community to manage
    def set_selected_community(self, cid: int):
        self.session.selected_community_id = cid
        self.show_admin_dashboard()

    # ======================================================
    # Screens
    # ======================================================
    def show_menu(self):
        self._push("menu", MenuView(self.page, self))

    def show_login(self):
        self._push("login", LoginView(self.page, controller=self, on_back_click=self.go_back))

    def show_signup(self):
        self._push("signup", SignupView(self.page, controller=self, on_back_click=self.go_back))

    def show_recover(self):
        self._push("recover", RecoverPasswordView(self.page, controller=self, on_back_click=self.go_back))

    def show_reset(self):
        self._push("reset", ResetPasswordView(self.page, controller=self, on_back_click=self.go_back))

    # ============================================
    # INFO CONTROL VIEW (Sensors + Actuators)
    # ============================================
    def show_info_control(self, e=None):
        '''
        Combined Sensors Info + Actuators 
        Control screen (ADMIN + TECH only).
        '''
        user = self.session.current_user
        if not user:
            return self.show_login()

        role = user.role.value.lower()

        # Determine community
        if role == "admin":
            cid = getattr(self.session, "selected_community_id", None)
            if cid is None:
                self._notify("Seleccione una comunidad primero.")
                return self.show_admin_dashboard()
        else:
            cid = user.community_id

        # Choose where the "Dashboard" button should go back to
        if role == "admin":
            back_dashboard = self.show_admin_dashboard
        elif role == "technician":
            back_dashboard = self.show_tecnico_dashboard
        else:
            back_dashboard = self.show_user_dashboard

        view = InfoControlView(
            page=self.page,
            controller=self,
            user=user,
            role=user.role.value,
            community_id=cid,
            on_dashboard=back_dashboard,
            on_alerts=self.show_alerts,
            on_logout=self.logout,
            on_settings=self.show_settings,
        )

        self._replace("info_control", view)

    # ============================================
    # HISTORY VIEW
    # ============================================
    def show_history(self, e=None):
        user = self.session.current_user
        if not user:
            return self.show_login()

        role = user.role.value.lower()

        # Community selection logic (admin must choose)
        if role == "admin":
            cid = getattr(self.session, "selected_community_id", None)
            if cid is None:
                self._notify("Seleccione una comunidad primero.")
                return self.show_admin_dashboard()
        else:
            cid = user.community_id

        # Choose dashboard return path
        if role == "admin":
            back = self.show_admin_dashboard
        elif role == "technician":
            back = self.show_tecnico_dashboard
        else:
            back = self.show_user_dashboard

        view = HistoryView(
            page=self.page,
            controller=self,
            user=user,
            role=user.role.value,
            community_id=cid,
            on_dashboard=back,
            on_alerts=self.show_alerts,
            on_logout=self.logout,
            on_settings=self.show_settings,
        )
        self._replace("history", view)


    # ============================================
    # USER MANAGEMENT VIEW
    # ============================================
    def show_user_management(self, e=None):
        user = self.session.current_user
        if not user:
            return self.show_login()

        if user.role.value.lower() != "admin":
            return self._notify("Solo administradores pueden gestionar usuarios.")

        view = UserManagementView(
            page=self.page,
            controller=self,
            user=user,
            role=user.role.value,
            on_dashboard=self.show_admin_dashboard,
            on_alerts=self.show_alerts,
            on_logout=self.logout,
            on_settings=self.show_settings,
        )

        self._replace("user_management", view)


    # ======================================================
    # Post-authentication navigation
    # ======================================================
    def show_dashboard(self, e=None):
        user = self.session.current_user
        if not user:
            return self.show_login()

        role = user.role.value

        if role == "NEIGHBOR":
            return self.show_user_dashboard()
        elif role == "ADMIN":
            return self.show_admin_dashboard()
        elif role == "TECHNICIAN":
            return self.show_tecnico_dashboard()
        
    def show_user_dashboard(self, e=None):
        user = self.session.current_user
        summary = self.dashboard_service.get_dashboard_summary(
            user=user,
            effective_community_id=user.community_id,
        ).to_dict()
        temp_series = self.dashboard_service.get_sensor_timeseries(user.community_id, "TEMPERATURE", "24h")
        hum_series = self.dashboard_service.get_sensor_timeseries(user.community_id, "HUMIDITY", "24h")
        alerts_data = self.dashboard_service.get_alert_chart_data(user.community_id, "7d")
        latest_temp = self.dashboard_service.get_latest_sensor_reading(user.community_id, "TEMPERATURE")
        latest_hum = self.dashboard_service.get_latest_sensor_reading(user.community_id, "HUMIDITY")
        latest_smoke = self.dashboard_service.get_latest_sensor_reading(user.community_id, "SMOKE")
        week_temp_stats = self.dashboard_service.get_basic_statistics(user.community_id, "TEMPERATURE", "7d")
        month_temp_stats = self.dashboard_service.get_basic_statistics(user.community_id, "TEMPERATURE", "30d")
        week_hum_stats = self.dashboard_service.get_basic_statistics(user.community_id, "HUMIDITY", "7d")
        month_hum_stats = self.dashboard_service.get_basic_statistics(user.community_id, "HUMIDITY", "30d")
        plate_history = self.dashboard_service.get_user_plate_history(user.id, user.community_id, 20)

        view = UserDashboardView(
            page=self.page,
            controller=self,
            user=user,
            role=user.role.value,
            community_id=user.community_id,
            summary=summary,
            temp_series=temp_series,
            hum_series=hum_series,
            alerts_data=alerts_data,
            latest_temp=latest_temp,
            latest_hum=latest_hum,
            latest_smoke=latest_smoke,
            week_temp_stats=week_temp_stats,
            month_temp_stats=month_temp_stats,
            week_hum_stats=week_hum_stats,
            month_hum_stats=month_hum_stats,
            plate_history=plate_history,

            # nav buttons
            on_settings=self.show_settings,
            on_alerts=self.show_alerts,
            on_dashboard=self.show_user_dashboard,
            on_logout=self.logout,
        )

        self.history = ["dashboard"]
        self._replace("dashboard", view)


    def show_tecnico_dashboard(self, e=None):
        user = self.session.current_user
        if not user:
            return self.show_login()

        # For technicians, effective community is always their own
        summary_dto = self.dashboard_service.get_dashboard_summary(
            user=user,
            effective_community_id=user.community_id,
        )
        summary = summary_dto.to_dict()

        view = TechnicianDashboardView(
            page=self.page,
            controller=self,
            user=user,
            role=user.role.value,
            community_id=user.community_id,
            summary=summary,
            temp_series=self.dashboard_service.get_sensor_timeseries(user.community_id, "TEMPERATURE", "24h"),
            hum_series=self.dashboard_service.get_sensor_timeseries(user.community_id, "HUMIDITY", "24h"),
            alert_chart=self.dashboard_service.get_alert_chart_data(user.community_id, "7d"),
            actuator_state=self.dashboard_service.get_actuator_state_summary(user.community_id),
            error_summary=self.dashboard_service.get_error_summary(user.community_id, "7d"),
            temp_stats=self.dashboard_service.get_basic_statistics(user.community_id, "TEMPERATURE", "24h"),
            sensor_options={
                "TEMPERATURE": self.dashboard_service.get_sensors_for_community_and_type(user.community_id, "TEMPERATURE"),
                "HUMIDITY": self.dashboard_service.get_sensors_for_community_and_type(user.community_id, "HUMIDITY"),
                "WIND": self.dashboard_service.get_sensors_for_community_and_type(user.community_id, "WIND"),
            },
            on_settings=self.show_settings,
            on_alerts=self.show_alerts,
            on_dashboard=self.show_tecnico_dashboard,
            on_logout=self.logout,
        )

        self.history = ["dashboard"]
        self._replace("dashboard", view)

    def show_admin_dashboard(self, e=None):
        user = self.session.current_user
        if not user:
            return self.show_login()

        # Admin must explicitly choose a community
        cid = self.session.selected_community_id

        if cid is None:
            # Show minimal view prompting the user to select a community
            prompt = ft.Text(
                "Seleccione una comunidad para continuar",
                size=18,
                weight=ft.FontWeight.BOLD,
                color=PRIMARY_GREEN,
            )

            # Show empty admin view with just the dropdown
            # NOTE: We use an empty summary so the dropdown still populates
            summary_dto = self.dashboard_service.get_dashboard_summary(
                user=user,
                effective_community_id=0
            )
            summary = summary_dto.to_dict()

            view = AdminDashboardView(
                page=self.page,
                controller=self,
                user=user,
                role=user.role.value,
                community_id=None,
                summary=summary,
                all_communities_overview=[],
                sensitive_summary={"total": 0, "by_community": {}},
            temp_line_series=[],
            hum_line_series=[],
            aggregation_period=self.admin_chart_period,
            on_settings=self.show_settings,
                on_alerts=self.show_alerts,
                on_dashboard=self.show_admin_dashboard,
                on_logout=self.logout,
            )
            
            self.history = ["dashboard"]
            self._replace("dashboard", view)
            return

        summary_dto = self.dashboard_service.get_dashboard_summary(
            user=user,
            effective_community_id=cid,
        )
        summary = summary_dto.to_dict()

        view = AdminDashboardView(
            page=self.page,
            controller=self,
            user=user,
            role=user.role.value,
            community_id=cid,
            summary=summary,
            all_communities_overview=self._build_admin_communities_overview(summary.get("available_communities", [])),
            sensitive_summary=self.dashboard_service.get_unknown_plate_events_summary(None, "7d"),
            temp_line_series=self._get_admin_aggregated_series(cid, "TEMPERATURE"),
            hum_line_series=self._get_admin_aggregated_series(cid, "HUMIDITY"),
            aggregation_period=self.admin_chart_period,
            on_settings=self.show_settings,
            on_alerts=self.show_alerts,
            on_dashboard=self.show_admin_dashboard,
            on_logout=self.logout,
        )
            
        self.history = ["dashboard"]
        self._replace("dashboard", view)

    def _get_admin_aggregated_series(self, community_id: int, sensor_type: str):
        options = self.dashboard_service.get_sensors_for_community_and_type(community_id, sensor_type)
        if not options:
            return []
        sensor_id = int(options[0]["sensor_id"])
        return self.dashboard_service.get_sensor_series_by_id(
            sensor_id,
            window=self.admin_chart_period,
            aggregate=True,
            aggregate_bucket="hour_2" if self.admin_chart_period == "24h" else "weekday",
        )

    def set_admin_chart_options(self, *, period: str | None = None):
        if period:
            self.admin_chart_period = str(period)
        self.show_admin_dashboard()

    def get_sensor_series_for_dashboard(self, sensor_id: int, aggregate: bool, window: str = "7d", aggregate_bucket: str = "weekday"):
        return self.dashboard_service.get_sensor_series_by_id(
            sensor_id,
            window=window,
            aggregate=aggregate,
            aggregate_bucket=aggregate_bucket,
        )

    def _build_admin_communities_overview(self, communities: list[int]) -> list[dict]:
        rows = []
        for community_id in communities:
            sensor_total = self.dashboard_service.get_dashboard_summary(
                user=self.session.current_user,
                effective_community_id=community_id,
            ).sensors_summary.get("total_sensors", 0)
            alerts_total = self.dashboard_service.get_alert_chart_data(community_id, "7d").get("total", 0)
            errors_total = self.dashboard_service.get_error_summary(community_id, "7d").get("total", 0)
            unknown_total = self.dashboard_service.get_unknown_plate_events_summary(community_id, "7d").get("total", 0)
            rows.append(
                {
                    "community_id": community_id,
                    "sensors": sensor_total,
                    "alerts_7d": alerts_total,
                    "errors_7d": errors_total,
                    "unknown_plates_7d": unknown_total,
                }
            )
        return rows

    
    def show_alerts(self, e=None):

        user = self.session.current_user
        if not user:
            return self.show_login()

        role = user.role.value.lower()

        # Keep automation/evaluation side effects for admin/technician flows.
        if role == "admin":
            cid = self.session.selected_community_id
            if cid is not None:
                self.dashboard.get_alerts(user, selected_community_id=cid)
        elif role == "technician":
            self.dashboard.get_alerts(user, selected_community_id=user.community_id)

        # Read/unread capable list for every role: always use user deliveries.
        alerts = self.alert_service.get_alert_deliveries_for_user(user.id)

        # route to dashboard
        if role == "admin":
            back_fn = self.show_admin_dashboard
        elif role == "technician":
            back_fn = self.show_tecnico_dashboard
        else:
            back_fn = self.show_user_dashboard

        # render view
        view = AlertsDashboardView(
            page=self.page,
            controller=self,
            user=user,
            role=user.role.value,
            alerts=alerts,
            on_dashboard=back_fn,       
            on_alerts=self.show_alerts,
            on_logout=self.logout,
            on_back=None,
            on_settings=self.show_settings,
            on_mark_read=self.mark_alert_as_read,
        )

        self._replace("alerts", view)

    def mark_alert_as_read(self, alert_id: int):
        user = self.session.current_user
        if not user:
            return self.show_login()
        ok = self.alert_service.mark_read(alert_id, user.id)
        self._notify("Alert marked as read." if ok else "Could not mark alert as read.")
        self.show_alerts()


    def show_settings(self, e=None):
        user = self.session.current_user
        if not user:
            return self.show_login()

        view = UserEditView(
            page=self.page,
            controller=self,
            user=user,
            role=user.role.value,
            on_dashboard=self.show_dashboard,
            on_settings=self.show_settings,
            on_alerts=self.show_alerts,
            on_logout=self.logout,
            plates=self.plate_service.list_user_plates(user.id) if user.id is not None else [],
        )

        self._replace("settings", view)

    def show_faqs(self):
        user = self.session.current_user
        if not user or user.role.value.lower() != "neighbor":
            return

        faqs = self.dashboard.get_faqs_for_community(user.community_id)

        view = FaqsView(
            page=self.page,
            controller=self,
            user=user,
            role=user.role.value,
            on_dashboard=self.show_user_dashboard,
            on_alerts=self.show_alerts,
            on_logout=self.logout,
            on_settings=self.show_settings,
            faqs=faqs,
            on_open_chat_from_faq=self.open_chat_from_faq,
        )
        self._replace("faqs", view)

    def show_chat_thread_list(self):
        user = self.session.current_user
        if not user:
            return
        role = user.role.value.lower()
        if role == "technician":
            threads = self.dashboard.get_chat_threads_for_technician(user.id)
            back_fn = self.show_tecnico_dashboard
            can_resolve = True
        elif role == "neighbor":
            threads = self.dashboard.get_chat_threads_for_neighbor(user.id)
            back_fn = self.show_user_dashboard
            can_resolve = False
        else:
            return

        view = ChatThreadListView(
            page=self.page,
            controller=self,
            user=user,
            role=user.role.value,
            on_dashboard=back_fn,
            on_alerts=self.show_alerts,
            on_logout=self.logout,
            on_back=back_fn,
            on_settings=self.show_settings,
            threads=threads,
            on_open_chat=self.show_chat_messages,
            on_resolve_chat=self.resolve_chat,
            can_resolve=can_resolve,
        )
        self._replace("chat_threads", view)

    def show_chat_messages(self, chat_id: str):
        user = self.session.current_user
        if not user:
            return self.show_login()

        chat = self.dashboard.get_chat_by_id(chat_id)
        if not chat:
            return self._notify("Chat no encontrado.")
        if not self._can_current_user_open_chat(chat):
            return self._notify("No tienes permiso para abrir este chat.")

        messages = self.dashboard.get_chat_messages(chat_id)

        # Back target depends on role
        if user.role.value.lower() == "technician":
            back_fn = self.show_chat_thread_list
        else:
            back_fn = self.show_chat_thread_list

        view = ChatMessagesView(
            page=self.page,
            chat_id=chat_id,
            current_user_role=user.role.value,
            title=chat.get("title", "Chat"),
            messages=messages,
            on_back=back_fn,
            on_send=lambda text: self.send_chat_message(chat_id, text),
            on_resolve=(lambda: self.resolve_chat(chat_id)) if user.role.value.lower() == "technician" else None,
        )

        self._replace("chat_messages", view)
    
    def open_chat_from_faq(self, faq_item):
        user = self.session.current_user
        if not user:
            return self.show_login()

        try:
            chat_id = self.dashboard.open_chat_from_faq(
                neighbor_id=user.id,
                community_id=user.community_id,
                faq_id=faq_item.id,
                faq_question=faq_item.question,
            )
        except ValueError as e:
            return self._notify(str(e))

        self.show_chat_messages(chat_id)
    
    def send_chat_message(self, chat_id: str, text: str):
        user = self.session.current_user
        if not user:
            return self.show_login()

        try:
            self.dashboard.send_chat_message(
                chat_id=chat_id,
                sender_id=user.id,
                sender_role=user.role.value,
                text=text,
            )
        except (PermissionError, ValueError) as exc:
            return self._notify(str(exc))

        self.show_chat_messages(chat_id)
    
    def resolve_chat(self, chat_id: str):
        user = self.session.current_user
        if not user:
            return self.show_login()

        if user.role.value.lower() != "technician":
            return self._notify("Solo un técnico puede resolver chats.")

        try:
            self.dashboard.resolve_chat(chat_id, technician_id=user.id)
        except (PermissionError, ValueError) as exc:
            return self._notify(str(exc))
        self._notify("Chat resuelto correctamente.")
        self.show_chat_thread_list()  

    def _can_current_user_open_chat(self, chat: dict) -> bool:
        user = self.session.current_user
        if not user:
            return False
        if user.role == RoleEnum.NEIGHBOR:
            return int(chat.get("created_by_user_id")) == int(user.id)
        if user.role == RoleEnum.TECHNICIAN:
            assigned_user_id = chat.get("assigned_user_id")
            if assigned_user_id is not None:
                return int(assigned_user_id) == int(user.id)
            return int(chat.get("community_id")) == int(user.community_id)
        return user.role == RoleEnum.ADMIN
   
    def get_kpis(self) -> dict:
        """
        Delegates KPI computation to DashboardController.
        """
        return self.dashboard.get_kpis()

    # ======================================================
    # View Callbacks (delegations to AuthController)
    # ======================================================
    def login(self, email, password):
        ok, msg, user = self.auth.login(email, password)
        self._notify(msg)

        if not ok:
            return
        else:
            # Successful login → dashboard
            return self.show_dashboard()

    def signup(self, name, community_id, email, password, dob, picture_path=None):
        
        result = self.auth.signup(
            name=name, 
            community_id=community_id,
            email=email,
            password=password, 
            dob=dob, 
            picture_temp_path=picture_path
        )

        if result is True:
            # Signup success → Login
            self._replace("login", LoginView(self.page, self, on_back_click=self.go_back))

            self.page.snack_bar = ft.SnackBar(
                ft.Text("Cuenta creada con éxito. Inicia sesión."),
                bgcolor=SUCCESS_GREEN
            )
            self.page.snack_bar.open = True
            self.page.update()
            return

        # Signup failed
        self.page.snack_bar = ft.SnackBar(
            ft.Text(result or "Error al registrarse."), 
            bgcolor=ERROR_RED
        )
        self.page.snack_bar.open = True
        self.page.update()

    def recover(self, email):
        ok, msg = self.auth.recover_password(email)

        # Show snackbar
        self.page.snack_bar = ft.SnackBar(
            ft.Text(msg),
            # Simulation of real-world dynamics: red means no 
            # email was sent, green means email was sent
            bgcolor=SUCCESS_GREEN if ok else ERROR_RED, 
        )
        self.page.snack_bar.open = True
        self.page.update()
    
        # Only navigate to reset if user exists
        if ok:
            # self.session.start_reset(email)
            self.show_reset()
        else:
            self.show_menu()

    def reset_password(self, pass1, pass2):
        result = self.auth.update_password(pass1, pass2)

        color = SUCCESS_GREEN if "éxito" in result.lower() else ERROR_RED
        self.page.snack_bar = ft.SnackBar(ft.Text(result), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()

        if "éxito" in result.lower():
            self.history = ["login"]
            self._replace("login", LoginView(self.page, self, on_back_click=self.go_back))  

    def update_profile(self, name: str, email: str):
        """
        Called from UserEditView when saving the profile.

        For this simulation:
        - Validate basic fields
        - Ensure email uniqueness
        - Update the in-memory User
        - Persist via UserRepository (self.auth.repo)
        """

        user = self.session.current_user
        if not user:
            return False, "No hay usuario en sesión."

        name = (name or "").strip()
        email = (email or "").strip().lower()

        if not name or not email:
            return False, "Nombre y correo son obligatorios."

        if "@" not in email or "." not in email:
            return False, "Formato de correo no válido."

        existing = self.auth.repo.find_by_email(email)
        if existing and getattr(existing, "id", None) != getattr(user, "id", None):
            return False, "Ya existe un usuario con ese correo."

        try:
            self.user_service.update_own_profile(user, fullname=name, email=email)
            return True, "Perfil actualizado correctamente."
        except Exception:
            return False, "Error tecnico al actualizar el perfil."

    def request_plate_registration(self, plate: str):
        user = self.session.current_user
        if not user:
            return False, "No hay usuario en sesion."
        try:
            self.plate_service.request_user_plate(
                user_id=int(user.id),
                community_id=int(user.community_id),
                plate=plate,
            )
            return True, "Matricula enviada para aprobacion."
        except Exception as exc:
            self.error_service.capture_exception(
                exc,
                source_layer="CONTROLLER",
                user_id=int(user.id) if user.id is not None else None,
                community_id=user.community_id,
                target_entity_type="allowed_plate",
            )
            return False, "No se pudo registrar la matricula."

    def deactivate_plate_registration(self, allowed_plate_id: int):
        user = self.session.current_user
        if not user:
            return False, "No hay usuario en sesion."
        try:
            self.plate_service.deactivate_user_plate(
                allowed_plate_id=int(allowed_plate_id),
                user_id=int(user.id),
                community_id=int(user.community_id),
            )
            return True, "Matricula desactivada."
        except Exception as exc:
            self.error_service.capture_exception(
                exc,
                source_layer="CONTROLLER",
                user_id=int(user.id) if user.id is not None else None,
                community_id=user.community_id,
                target_entity_type="allowed_plate",
                target_entity_id=int(allowed_plate_id),
            )
            return False, "No se pudo desactivar la matricula."

    def approve_plate_registration(self, allowed_plate_id: int):
        user = self.session.current_user
        if not user:
            return False, "No hay usuario en sesion."
        try:
            role = user.role if isinstance(user.role, RoleEnum) else RoleEnum(user.role)
            self.plate_service.approve_plate(
                allowed_plate_id=int(allowed_plate_id),
                actor_id=int(user.id),
                actor_role=role,
                community_id=user.community_id,
            )
            return True, "Matricula aprobada."
        except Exception as exc:
            self.error_service.capture_exception(
                exc,
                source_layer="CONTROLLER",
                user_id=int(user.id) if user.id is not None else None,
                community_id=user.community_id,
                target_entity_type="allowed_plate",
                target_entity_id=int(allowed_plate_id),
            )
            return False, "No se pudo aprobar la matricula."

    def deny_plate_registration(self, allowed_plate_id: int):
        user = self.session.current_user
        if not user:
            return False, "No hay usuario en sesion."
        try:
            role = user.role if isinstance(user.role, RoleEnum) else RoleEnum(user.role)
            self.plate_service.deny_plate(
                allowed_plate_id=int(allowed_plate_id),
                actor_id=int(user.id),
                actor_role=role,
                community_id=None,
            )
            return True, "Solicitud de matricula denegada."
        except Exception as exc:
            self.error_service.capture_exception(
                exc,
                source_layer="CONTROLLER",
                user_id=int(user.id) if user.id is not None else None,
                community_id=getattr(user, "community_id", None),
                target_entity_type="allowed_plate",
                target_entity_id=int(allowed_plate_id),
            )
            return False, "No se pudo denegar la matricula."

    def get_pending_plate_requests_for_admin(self):
        user = self.session.current_user
        if not user:
            return []
        role_value = user.role.value if hasattr(user.role, "value") else str(user.role)
        if role_value != "ADMIN":
            return []
        return self.plate_service.list_pending_plates(None)
  

    def logout(self, e=None):        
        # clear session
        self.session.logout()

        # clear navigation history
        self.history = []

        # Reset page UI
        self.page.controls.clear()
        self.show_menu()    # go to ViewMenu (your first screen)
        self.page.update()

    # ======================================================
    # Navigation callbacks from views
    # ======================================================
    def go_login(self): self.show_login()
    def go_signup(self): self.show_signup()
    def go_recover(self): self.show_recover()
    def go_reset(self): self.show_reset()

    # ======================================================
    # BACK navigation
    # ======================================================
    def go_back(self):
        if not self.history:
            return

        self.history.pop()

        if not self.history:
            return self._replace("menu", MenuView(self.page, self))

        last = self.history[-1]

        if last == "menu":
            self._replace("menu", MenuView(self.page, self))
        elif last == "login":
            self._replace("login", LoginView(self.page, self, on_back_click=self.go_back))
        elif last == "signup":
            self._replace("signup", SignupView(self.page, self, on_back_click=self.go_back))
        elif last == "recover":
            self._replace("recover", RecoverPasswordView(self.page, self, on_back_click=self.go_back))
        elif last == "reset":
            self._replace("reset", ResetPasswordView(self.page, self, on_back_click=self.go_back))
        elif last == "dashboard":
            self.show_dashboard()
