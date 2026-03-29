import flet as ft

# Controller imports
from app.controller.auth_controller import AuthController, Session
from app.controller.dashboard_controller import DashboardController

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

# Service imports
from app.service.alert_service import AlertService
from app.service.dashboard_service import DashboardService
from app.service.monitoring_service import MonitoringService
from app.service.actuator_service import ActuatorService

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

        # Dashboard summary
        self.sensor_repo = SensorRepository()
        self.actuator_repo = ActuatorRepository()
        self.log_repo = LogRepository()
        self.reading_repo = ReadingRepository()
        self.actuator_service = ActuatorService(self.actuator_repo)
        self.monitoring_service = MonitoringService(
            self.sensor_repo,
            self.reading_repo,
            self.alert_repo,
            self.log_repo,
        )
        self.faq_repo = FAQRepository()
        self.chat_repo = ChatRepository()
        self.dashboard = DashboardController(
            self.alert_service, 
            self.monitoring_service, 
            session, 
            self.actuator_service,
            self.log_repo,
            user_repository=auth_controller.repo,
            faq_repository=self.faq_repo,          # to be implemented
            chat_repository=self.chat_repo,         # to be implemented
        )
        self.dashboard_service = DashboardService(
            self.sensor_repo,
            self.actuator_repo,
            self.alert_repo,
            self.log_repo,
            self.reading_repo,
        )

        self.session = session

        self.history = []             # navigation stack
        self.page.assets_dir = "app/assets"

    # ======================================================
    # Internal navigation utilities
    # ======================================================
    def _push(self, name: str, view:  ft.UserControl):
        if not self.history or self.history[-1] != name:
            self.history.append(name)

        self.page.controls.clear()
        self.page.add(view)
        self.page.update()

    def _replace(self, name: str, view:  ft.UserControl):
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

        view = UserDashboardView(
            page=self.page,
            controller=self,
            user=user,
            role=user.role.value,
            community_id=user.community_id,

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
            on_settings=self.show_settings,
            on_alerts=self.show_alerts,
            on_dashboard=self.show_admin_dashboard,
            on_logout=self.logout,
        )
            
        self.history = ["dashboard"]
        self._replace("dashboard", view)

    
    def show_alerts(self, e=None):
        print(">>> showing alerts")

        user = self.session.current_user
        if not user:
            return self.show_login()

        role = user.role.value.lower()

        # determine community id based on role
        if role == "admin":
            cid = self.session.selected_community_id
            if cid is None:
                # Admin must select a community first
                self._notify("Seleccione una comunidad primero.")
                return self.show_admin_dashboard()
        else:
            # Technician / Neighbor -> always fixed community
            cid = user.community_id

        alerts = self.dashboard.get_alerts(user, selected_community_id=cid)
        print(f">>> fetched {len(alerts)} alerts for community {cid}")
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
        )

        self._replace("alerts", view)


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
        )

        self._replace("settings", view)

    def show_actuator_history(self, actuator_id: int):
        logs = self.log_repo.all()

        actuator_logs = [
            l for l in logs
            if l.get("category") == "ACTUATOR"
            and str(l.get("target_id")) == str(actuator_id)
        ]

        view = AlertsDashboardView(
            page=self.page,
            controller=self,
            user=self.session.current_user,
            role=self.session.current_user.role,
            alerts=actuator_logs,  # reuse alerts-style list
            on_dashboard=self.show_dashboard,
            on_alerts=self.show_alerts,
            on_logout=self.logout,
            on_back=self.show_info_control,
        )

        self._replace("actuator_history", view)

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
        if not user or user.role.value.lower() != "technician":
            return

        threads = self.dashboard.get_chat_threads_for_technician(user.id)

        view = ChatThreadListView(
            page=self.page,
            controller=self,
            user=user,
            role=user.role.value,
            on_dashboard=self.show_tecnico_dashboard,
            on_alerts=self.show_alerts,
            on_logout=self.logout,
            on_back=self.show_tecnico_dashboard,
            on_settings=self.show_settings,
            threads=threads,
            on_open_chat=self.show_chat_messages,
            on_resolve_chat=self.resolve_chat,
        )
        self._replace("chat_threads", view)

    def show_chat_messages(self, chat_id: str):
        user = self.session.current_user
        if not user:
            return self.show_login()

        chat = self.dashboard.get_chat_by_id(chat_id)
        if not chat:
            return self._notify("Chat no encontrado.")

        messages = self.dashboard.get_chat_messages(chat_id)

        # Back target depends on role
        if user.role.value.lower() == "technician":
            back_fn = self.show_chat_thread_list
        else:
            back_fn = self.show_faqs

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

        self.dashboard.send_chat_message(
            chat_id=chat_id,
            sender_id=user.id,
            sender_role=user.role.value.lower(),
            text=text,
        )

        self.show_chat_messages(chat_id)
    
    def resolve_chat(self, chat_id: str):
        user = self.session.current_user
        if not user:
            return self.show_login()

        if user.role.value.lower() != "technician":
            return self._notify("Solo un técnico puede resolver chats.")

        self.dashboard.resolve_chat(chat_id, technician_id=user.id)
        self._notify("Chat resuelto correctamente.")
        self.show_chat_thread_list()  
   
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

        # Check if another user already has this email
        existing = self.auth.repo.find_by_email(email)
        if existing and getattr(existing, "id", None) != getattr(user, "id", None):
            return False, "Ya existe un usuario con ese correo."

        # Update the current user
        user.name = name
        user.email = email

        # Persist changes
        self.auth.repo.save()

        return True, "Perfil actualizado correctamente."
  

    def logout(self, e=None):
        print(">>> LOGOUT")
        
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
