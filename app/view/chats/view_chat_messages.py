from dataclasses import dataclass
from typing import Callable, List, Optional

import flet as ft

from app.view.theme import BRAND_ACCENT_BLUE, FULL_BLACK, PRIMARY_GREEN, WHITE


@dataclass(frozen=True)
class ChatMessageItem:
    sender_name: str
    sender_role: str
    text: str
    timestamp: str


class ChatMessagesView(ft.UserControl):
    def __init__(
        self,
        page: ft.Page,
        chat_id: str,
        current_user_role: str,
        on_back: Callable[[], None],
        on_send: Callable[[str], None],
        on_resolve: Optional[Callable[[], None]] = None,
        title: str = "Chat",
        messages: Optional[List[ChatMessageItem]] = None,
    ):
        super().__init__()
        self.page = page
        self.chat_id = chat_id
        self.current_user_role = (current_user_role or "").upper()
        self.on_back = on_back
        self.on_send = on_send
        self.on_resolve = on_resolve
        self._title = title
        self._messages = messages or []

        self._input = ft.TextField(
            hint_text="Message",
            expand=True,
            dense=True,
            border_radius=24,
            on_submit=self._handle_send,
        )
        self._messages_list = ft.ListView(
            expand=True,
            spacing=8,
            padding=ft.padding.only(left=12, right=12, top=12, bottom=12),
            auto_scroll=True,
        )
        self._rebuild_messages()

    def _handle_send(self, e: ft.ControlEvent) -> None:
        text = (self._input.value or "").strip()
        if not text:
            return
        self._input.value = ""
        self.on_send(text)

    def _rebuild_messages(self) -> None:
        self._messages_list.controls.clear()
        for message in self._messages:
            self._messages_list.controls.append(self._bubble(message))

    def _bubble(self, message: ChatMessageItem) -> ft.Control:
        mine = (message.sender_role or "").upper() == self.current_user_role
        bubble_color = "#D9FDD3" if mine else WHITE
        align = ft.MainAxisAlignment.END if mine else ft.MainAxisAlignment.START
        radius = ft.border_radius.only(
            top_left=16,
            top_right=16,
            bottom_left=16 if mine else 4,
            bottom_right=4 if mine else 16,
        )

        bubble = ft.Container(
            bgcolor=bubble_color,
            border_radius=radius,
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            width=430,
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Text(message.sender_name, size=11, color=BRAND_ACCENT_BLUE, weight=ft.FontWeight.BOLD),
                    ft.Text(message.text, size=14, color=FULL_BLACK, selectable=True),
                    ft.Text(str(message.timestamp).replace("T", " ")[:19], size=10, color="#63706C", text_align=ft.TextAlign.RIGHT),
                ],
            ),
        )
        return ft.Row(alignment=align, controls=[bubble])

    def build(self) -> ft.Control:
        actions = [
            ft.IconButton(icon=ft.icons.ARROW_BACK, icon_color=PRIMARY_GREEN, on_click=lambda e: self.on_back())
        ]
        if self.on_resolve and self.current_user_role == "TECHNICIAN":
            actions.append(
                ft.TextButton(
                    text="Resolve",
                    icon=ft.icons.CHECK,
                    on_click=lambda e: self.on_resolve(),
                )
            )

        return ft.Container(
            width=980,
            height=640,
            bgcolor="#ECE5DD",
            border_radius=16,
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Container(
                        bgcolor=WHITE,
                        padding=12,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Row(
                                    spacing=10,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.CircleAvatar(radius=18, bgcolor=PRIMARY_GREEN, content=ft.Text(self._title[:1].upper(), color=WHITE)),
                                        ft.Text(self._title, size=16, weight=ft.FontWeight.BOLD, color=PRIMARY_GREEN),
                                    ],
                                ),
                                ft.Row(controls=actions),
                            ],
                        ),
                    ),
                    ft.Container(expand=True, content=self._messages_list),
                    ft.Container(
                        bgcolor="#F7F7F7",
                        padding=10,
                        content=ft.Row(
                            spacing=8,
                            controls=[
                                self._input,
                                ft.IconButton(
                                    icon=ft.icons.SEND,
                                    icon_color=PRIMARY_GREEN,
                                    on_click=self._handle_send,
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )
