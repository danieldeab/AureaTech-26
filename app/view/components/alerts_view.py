# app/view/components/alerts_view.py

import flet as ft
from app.model.enums import SeverityEnum
from app.view.theme import (
    PRIMARY_GREEN,
    LIGHT_GREEN,
    ERROR_RED,
    WARNING_YELLOW,
    INFO_BLUE,
    WHITE,
)


# ============================================================
# ICON FOR SINGLE ALERT BOX
# ============================================================

def bullet_icon(bg, fg):
    """ Small circular icon with exclamation mark. """
    return ft.Stack(
        controls=[
            ft.Container(width=22, height=22, bgcolor=fg, border_radius=11),
            ft.Container(
                width=22, height=22,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[ft.Text("!", color=bg, size=14, weight=ft.FontWeight.BOLD)],
                ),
            ),
        ]
    )


# ============================================================
# FULL ALERT BOX COMPONENT
# ============================================================

def AlertBox(message, bg, fg, dense=False):
    """
    Full alert visual card:
    - colored background
    - rounded edges
    - bullet icon
    - alert message
    """
    return ft.Container(
        bgcolor=bg,
        border_radius=20,
        padding=ft.padding.symmetric(
            14 if not dense else 8,
            12 if not dense else 8,
        ),
        content=ft.Row(
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                bullet_icon(bg, fg),
                ft.Text(message, color=fg, size=16 if not dense else 14),
            ],
        ),
    )


# ============================================================
# ALERTS LIST (SCROLLABLE)
# ============================================================

class AlertsList(ft.UserControl):
    """
    Scrollable list of AlertBox entries.
    The controller or dashboard passes a list of Alert objects.
    """

    def __init__(self, alerts, on_mark_read=None):
        super().__init__()
        self.alerts = alerts    # Expecting iterable of Alert objects or dict-like items
        self.on_mark_read = on_mark_read

    def build(self):
        alert_cards = []

        for a in self.alerts:
            if isinstance(a, dict):
                severity = a.get("severity", SeverityEnum.INFO)
                message = a.get("message") or a.get("description") or "Alerta"
                created_at = a.get("created_at") or a.get("timestamp")
                unread = not bool(a.get("read_status", False))
                alert_id = a.get("alert_id")
                action_required = bool(a.get("action_required", False)) or str(a.get("alert_type", "")).lower() == "unauthorized_plate"
            else:
                severity = getattr(a, "severity", SeverityEnum.INFO)
                message = getattr(a, "message", "Alerta")
                created_at = getattr(a, "created_at", None)
                unread = False
                alert_id = None
                action_required = False

            if not isinstance(severity, SeverityEnum):
                try:
                    severity = SeverityEnum(str(severity))
                except ValueError:
                    severity = SeverityEnum.INFO

            if severity == SeverityEnum.CRIT:
                card = AlertBox(message, ERROR_RED, WHITE)
            elif severity == SeverityEnum.WARN:
                card = AlertBox(message, WARNING_YELLOW, PRIMARY_GREEN)
            else:
                card = AlertBox(message, INFO_BLUE, PRIMARY_GREEN)

            details = []
            if created_at:
                details.append(ft.Text(str(created_at).replace("T", " ")[:19], size=11, color=PRIMARY_GREEN))
            if action_required:
                details.append(ft.Text("Action required", size=11, color=ERROR_RED, weight=ft.FontWeight.BOLD))

            row_controls = [card, *details]
            if unread and self.on_mark_read and alert_id is not None:
                row_controls.append(
                    ft.TextButton(
                        text="Mark as read",
                        on_click=lambda e, aid=alert_id: self.on_mark_read(aid),
                    )
                )
            alert_cards.append(ft.Column(spacing=6, controls=row_controls))

        if not alert_cards:
            alert_cards.append(ft.Text("No alerts.", size=12, color=PRIMARY_GREEN))

        return ft.Column(
            spacing=15,
            controls=alert_cards,
        )
