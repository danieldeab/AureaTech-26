# app/view/components/alerts_view.py

import flet as ft
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

    def __init__(self, alerts):
        super().__init__()
        self.alerts = alerts    # Expecting iterable of Alert objects or dict-like items

    def build(self):
        alert_cards = []

        for a in self.alerts:
            # For now, we assume each alert has: message, type
            # Later you can enhance it with timestamps, severity, icons, etc.
            severity = getattr(a, "severity", "info")
            message = getattr(a, "message", "Alerta")

            if severity == "error":
                card = AlertBox(message, ERROR_RED, WHITE)
            elif severity == "warning":
                card = AlertBox(message, WARNING_YELLOW, PRIMARY_GREEN)
            elif severity == "success":
                card = AlertBox(message, LIGHT_GREEN, PRIMARY_GREEN)
            else:
                card = AlertBox(message, INFO_BLUE, PRIMARY_GREEN)

            alert_cards.append(card)

        return ft.Column(
            spacing=15,
            controls=alert_cards,
        )
