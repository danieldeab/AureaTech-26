# app/view/chats/view_chat_messages.py

import flet as ft
from dataclasses import dataclass
from typing import Callable, List, Optional


@dataclass(frozen=True)
class ChatMessageItem:
    sender_name: str
    sender_role: str          # "NEIGHBOR" / "TECHNICIAN"
    text: str
    timestamp: str            # formatted for UI


class ChatMessagesView(ft.UserControl):
    """
    Chat message screen for neighbor or technician.
    - Renders messages
    - Input box + send button
    - Optional resolve button (for technicians)
    """

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
        self._messages: List[ChatMessageItem] = messages or []

        self._input = ft.TextField(
            hint_text="Type a message…",
            expand=True,
            on_submit=self._handle_send,
        )

        self._messages_list = ft.ListView(expand=True, spacing=8, auto_scroll=True)

        self._rebuild_messages()

    def set_messages(self, messages: List[ChatMessageItem]) -> None:
        self._messages = messages
        self._rebuild_messages()
        self.update()

    def _handle_send(self, e: ft.ControlEvent) -> None:
        text = (self._input.value or "").strip()
        if not text:
            return
        self._input.value = ""
        self.on_send(text)
        self.update()

    def _rebuild_messages(self) -> None:
        self._messages_list.controls.clear()
        for m in self._messages:
            self._messages_list.controls.append(self._bubble(m))

    def _bubble(self, m: ChatMessageItem) -> ft.Control:
        mine = (m.sender_role or "").upper() == self.current_user_role
        align = ft.MainAxisAlignment.END if mine else ft.MainAxisAlignment.START

        bubble = ft.Container(
            padding=10,
            border_radius=12,
            bgcolor=ft.Colors.BLUE_50 if mine else ft.Colors.GREY_100,
            content=ft.Column(
                spacing=2,
                controls=[
                    ft.Text(f"{m.sender_name} • {m.timestamp}", size=11, italic=True),
                    ft.Text(m.text, selectable=True),
                ],
            ),
        )

        return ft.Row(alignment=align, controls=[bubble])

    def build(self) -> ft.Control:
        top_actions = [
            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: self.on_back())
        ]

        if self.on_resolve and self.current_user_role == "TECHNICIAN":
            top_actions.append(
                ft.FilledButton(
                    text="Resolve",
                    icon=ft.Icons.CHECK,
                    on_click=lambda e: self.on_resolve(),
                )
            )

        return ft.Column(
            expand=True,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(self._title, size=18, weight=ft.FontWeight.BOLD),
                        ft.Row(controls=top_actions),
                    ],
                ),
                ft.Divider(height=1),
                self._messages_list,
                ft.Divider(height=1),
                ft.Row(
                    controls=[
                        self._input,
                        ft.IconButton(icon=ft.Icons.SEND, on_click=self._handle_send),
                    ]
                ),
            ],
        )