# app/view/lists/view_chat_thread_list.py

import flet as ft
from dataclasses import dataclass
from typing import Callable, List, Optional

from app.view.base.view_base_list import BaseListView
from app.view.theme import PRIMARY_GREEN


@dataclass(frozen=True)
class ChatThreadItem:
    chat_id: str
    title: str               # e.g., FAQ question/theme
    neighbor_name: str
    status: str              # "OPEN", "IN_PROGRESS" or "CLOSED"
    last_message_preview: str
    last_updated: str        # already formatted string for UI


class ChatThreadListView(BaseListView):
    """
    Technician-facing list of open + past chats.
    Includes:
      - filter chips (Open / Resolved / All)
      - resolve button for open chats
      - click row to open chat
    """

    def __init__(
        self,
        page: ft.Page,
        controller,
        user,
        role: str,
        on_dashboard,
        on_alerts,
        on_logout,
        on_open_chat: Callable[[str], None],
        on_resolve_chat: Callable[[str], None],
        can_resolve: bool = True,
        on_back=None,
        on_settings=None,
        title: str = "Chats",
        threads: Optional[List[ChatThreadItem]] = None,
    ):
        super().__init__(
            page=page,
            controller=controller,
            user=user,
            role=role,
            on_dashboard=on_dashboard,
            on_alerts=on_alerts,
            on_logout=on_logout,
            on_back=on_back,
            on_settings=on_settings,
            title=title,
        )

        self._all_threads: List[ChatThreadItem] = threads or []
        self._filtered: List[ChatThreadItem] = list(self._all_threads)

        self._on_open_chat = on_open_chat
        self._on_resolve_chat = on_resolve_chat
        self._can_resolve = can_resolve

        self._filter = "OPEN"  # default

        self._list_column = ft.Column(spacing=10, height=420, scroll=ft.ScrollMode.AUTO)
        self._apply_filter()

    def set_threads(self, threads: List[ChatThreadItem]) -> None:
        self._all_threads = threads
        self._apply_filter()

    def build_list(self) -> ft.Control:
        return ft.Column(
            spacing=10,
            controls=[
                self._filter_chips(),
                ft.Divider(height=1),
                self._list_column,
            ],
        )

    def _set_filter(self, value: str) -> None:
        self._filter = value
        self._apply_filter()
        self.page.update()

    def _filter_chips(self):
        def set_filter(value: str):
            self._filter = value
            self._apply_filter()
            for chip in chips.controls:
                chip.selected = chip.data == value
            self.update()

        chips = ft.Row(
            spacing=12,
            controls=[
                ft.Chip(label=ft.Text("Open"), selected=self._filter == "OPEN", data="OPEN", on_select=lambda e: set_filter(e.control.data)),
                ft.Chip(label=ft.Text("In progress"), selected=self._filter == "IN_PROGRESS", data="IN_PROGRESS", on_select=lambda e: set_filter(e.control.data)),
                ft.Chip(label=ft.Text("Closed"), selected=self._filter == "CLOSED", data="CLOSED", on_select=lambda e: set_filter(e.control.data)),
                ft.Chip(label=ft.Text("All"), selected=self._filter == "ALL", data="ALL", on_select=lambda e: set_filter(e.control.data)),
            ],
        )
        return chips

    def _apply_filter(self) -> None:
        if self._filter == "ALL":
            self._filtered = list(self._all_threads)
        else:
            self._filtered = [t for t in self._all_threads if normalize_chat_status(t.status) == self._filter]

        self._rebuild_list()

    def _rebuild_list(self) -> None:
        self._list_column.controls.clear()

        if not self._filtered:
            self._list_column.controls.append(
                ft.Container(
                    padding=12,
                    content=ft.Text("No chats to show for this filter."),
                )
            )
            return

        for t in self._filtered:
            self._list_column.controls.append(self._thread_card(t))

    def _thread_card(self, t: ChatThreadItem) -> ft.Control:
        status = normalize_chat_status(t.status)
        is_open = status in {"OPEN", "IN_PROGRESS"}

        resolve_btn = (
            ft.OutlinedButton(
                text="Resolve",
                icon=ft.icons.CHECK_CIRCLE_OUTLINE,
                on_click=lambda e, cid=t.chat_id: self._on_resolve_chat(cid),
                disabled=not is_open,
            )
            if self._can_resolve
            else ft.Container(width=0)
        )

        return ft.Container(
            bgcolor="#FFFFFF",
            border_radius=10,
            padding=12,
            on_click=lambda e, cid=t.chat_id: self._on_open_chat(cid),
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(t.title, weight=ft.FontWeight.BOLD, color=PRIMARY_GREEN),
                            ft.Text(status, color=PRIMARY_GREEN if is_open else None, size=12),
                        ],
                    ),
                    ft.Text(f"Neighbor: {t.neighbor_name}", size=12),
                    ft.Text(t.last_message_preview, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS, size=13),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(str(t.last_updated).replace("T", " ")[:19], size=11, italic=True),
                            resolve_btn,
                        ],
                    ),
                ],
            ),
        )


def normalize_chat_status(status: str) -> str:
    normalized = (status or "").strip().upper()
    if normalized == "RESOLVED":
        return "CLOSED"
    if normalized in {"OPEN", "IN_PROGRESS", "CLOSED"}:
        return normalized
    return "OPEN"
