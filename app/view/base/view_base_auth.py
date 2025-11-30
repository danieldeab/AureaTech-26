import os
import flet as ft
from app.view.theme import (
    PRIMARY_GREEN,
    BACK_BLUE,
    WHITE,
    BORDER_SOFT,
    PANEL_W,
    PANEL_H,
    BG_CARD_PRIMARY,
)


class ViewBaseAuth(ft.UserControl):
    """
    Base class for all authentication pages.

    Child classes must override:
        - build_body(self) -> ft.Control

    This base handles:
        - Centered auth card (fixed PANEL_W x PANEL_H)
        - Title + optional subtitle
        - Back button on top-left
        - Smooth vertical scrolling *inside* the card
    """

    def __init__(self, page: ft.Page, controller,
                 title: str = "",
                 subtitle: str = "",
                 show_back: bool = True):
        super().__init__()
        self.page = page
        self.controller = controller
        self.title = title
        self.subtitle = subtitle
        self.show_back = show_back

    # ---------------------------------------------------------
    # Methods for child classes
    # ---------------------------------------------------------
    def build_body(self) -> ft.Control:
        """Return the main content (fields, buttons, etc.)."""
        raise NotImplementedError("Auth view must implement build_body().")

    # ---------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------
    def _make_back_button(self):
        if not self.show_back:
            return None

        back_icon = ft.Image(
            src=os.path.join(self.page.assets_dir, "back.png"),
            width=26,
            height=26,
            error_content=ft.Text(
                "<",
                color=BACK_BLUE,
                size=26,
                weight=ft.FontWeight.BOLD,
            ),
        )

        return ft.GestureDetector(
            on_tap=lambda e: self.controller.go_back(),
            content=ft.Container(padding=6, content=back_icon),
        )

    def _make_title_area(self):
        title_controls = []

        if self.title:
            title_controls.append(
                ft.Text(
                    self.title,
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=PRIMARY_GREEN,
                )
            )

        if self.subtitle:
            title_controls.append(
                ft.Text(
                    self.subtitle,
                    size=14,
                    color=PRIMARY_GREEN,
                )
            )

        if not title_controls:
            return None

        return ft.Column(
            controls=title_controls,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        )

    # ---------------------------------------------------------
    # Template method
    # ---------------------------------------------------------
    def build(self):
        title_area = self._make_title_area()
        body_area = self.build_body()
        back_btn = self._make_back_button()

        # This Column is the ONLY scrollable container.
        scrollable_column = ft.Column(
            controls=[
                *( [title_area] if title_area else [] ),
                ft.Container(height=22),
                body_area,
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            scroll=ft.ScrollMode.ALWAYS,   # smooth scroll inside card
        )

        card = ft.Container(
            width=PANEL_W,
            height=PANEL_H,
            bgcolor=BG_CARD_PRIMARY or WHITE,
            border_radius=22,
            border=ft.border.all(1, BORDER_SOFT),
            padding=ft.padding.only(top=36, bottom=24, left=32, right=32),
            content=ft.Stack(
                controls=[
                    # Scrollable content
                    ft.Container(
                        expand=True,
                        alignment=ft.alignment.top_center,
                        content=scrollable_column,
                    ),

                    # Back button overlay
                    ft.Container(
                        content=back_btn,
                        left=16,
                        top=12,
                    ) if back_btn else None,
                ]
            ),
        )

        # Let UIController position this card; we just return it.
        return card
