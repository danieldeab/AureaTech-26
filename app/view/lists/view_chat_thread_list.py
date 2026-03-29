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
    status: str              # "OPEN" or "RESOLVED"
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

        self._filter = "OPEN"  # default

        self._chips = ft.Row(
            spacing=8,
            controls=[
                ft.FilterChip(
                    label=ft.Text("Open"),
                    selected=True,
                    on_select=lambda e: self._set_filter("OPEN"),
                ),
                ft.FilterChip(
                    label=ft.Text("Resolved"),
                    selected=False,
                    on_select=lambda e: self._set_filter("RESOLVED"),
                ),
                ft.FilterChip(
                    label=ft.Text("All"),
                    selected=False,
                    on_select=lambda e: self._set_filter("ALL"),
                ),
            ],
        )

        self._list_column = ft.Column(spacing=10, expand=True)
        self._apply_filter()

    def set_threads(self, threads: List[ChatThreadItem]) -> None:
        self._all_threads = threads
        self._apply_filter()

    def build_list(self) -> ft.Control:
        return ft.Column(
            expand=True,
            spacing=10,
            controls=[
                self._chips,
                ft.Divider(height=1),
                self._list_column,
            ],
        )

    def _set_filter(self, value: str) -> None:
        self._filter = value

        # Update chip selection
        for chip in self._chips.controls:
            label = chip.label.value.upper()
            if "OPEN" in label:
                chip.selected = (value == "OPEN")
            elif "RESOLVED" in label:
                chip.selected = (value == "RESOLVED")
            elif "ALL" in label:
                chip.selected = (value == "ALL")

        self._apply_filter()
        self.page.update()

    def _apply_filter(self) -> None:
        if self._filter == "ALL":
            self._filtered = list(self._all_threads)
        else:
            self._filtered = [t for t in self._all_threads if t.status.upper() == self._filter]

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
        is_open = (t.status.upper() == "OPEN")

        resolve_btn = ft.OutlinedButton(
            text="Resolve",
            icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
            on_click=lambda e, cid=t.chat_id: self._on_resolve_chat(cid),
            disabled=not is_open,
        )

        return ft.Card(
            content=ft.Container(
                padding=12,
                on_click=lambda e, cid=t.chat_id: self._on_open_chat(cid),
                content=ft.Column(
                    spacing=6,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(t.title, weight=ft.FontWeight.BOLD),
                                ft.Text(t.status, color=PRIMARY_GREEN if is_open else None),
                            ],
                        ),
                        ft.Text(f"Neighbor: {t.neighbor_name}"),
                        ft.Text(t.last_message_preview, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(t.last_updated, size=12, italic=True),
                                resolve_btn,
                            ],
                        ),
                    ],
                ),
            )
        )