# app/view/lists/view_faqs.py

import flet as ft
from dataclasses import dataclass
from typing import Callable, List, Optional

from app.view.base.view_base_list import BaseListView
from app.view.theme import BRAND_ACCENT_BLUE, BRAND_BACKGROUND, BRAND_BACKGROUND, BRAND_DARK_GREY, BRAND_LIGHT_GREY, BRAND_LIGHT_GREY, PRIMARY_GREEN


@dataclass(frozen=True)
class FaqItem:
    id: str
    question: str
    answer: str


def _normalize(s: str) -> str:
    return " ".join((s or "").casefold().split())


def _cheap_fuzzy_score(query: str, text: str) -> float:
    """
    Simple, dependency-free fuzzy score in [0, 1].
    Not state-of-the-art, but OK as UI placeholder until you plug RapidFuzz.
    """
    q = _normalize(query)
    t = _normalize(text)
    if not q:
        return 1.0
    if q in t:
        return 1.0

    q_tokens = set(q.split())
    t_tokens = set(t.split())
    if not q_tokens or not t_tokens:
        return 0.0

    overlap = len(q_tokens & t_tokens) / max(len(q_tokens), 1)
    coverage = len(q_tokens & t_tokens) / max(len(t_tokens), 1)
    return 0.7 * overlap + 0.3 * coverage


class FaqsView(BaseListView):
    """
    Neighbor-facing FAQ list scoped to a community.
    - Search bar with fuzzy-ish filtering
    - Per FAQ: button to open a chat (callback injected)
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
        on_open_chat_from_faq: Callable[[FaqItem], None],
        on_settings=None,
        title: str = "FAQs",
        faqs: Optional[List[FaqItem]] = None,
    ):
        super().__init__(
            page=page,
            controller=controller,
            user=user,
            role=role,
            on_dashboard=on_dashboard,
            on_alerts=on_alerts,
            on_logout=on_logout,
            on_settings=on_settings,
            title=title,
        )

        self._all_faqs: List[FaqItem] = faqs or []
        self._filtered: List[FaqItem] = list(self._all_faqs)
        self._on_open_chat_from_faq = on_open_chat_from_faq

        self._search = ft.TextField(
            hint_text="Search FAQs…",
            hint_style=ft.TextStyle(color=BRAND_ACCENT_BLUE),
            color=BRAND_DARK_GREY,
            prefix_icon=ft.icons.SEARCH,
            on_change=self._on_search_change,
            expand=True,
        )

        self._list_column = ft.Column(spacing=10, expand=True)

        self._rebuild_list()

    def set_faqs(self, faqs: List[FaqItem]) -> None:
        self._all_faqs = faqs
        self._apply_filter(self._search.value or "")

    def build_list(self) -> ft.Control:
        return ft.Column(
            expand=True,
            spacing=10,
            controls=[
                ft.Row(controls=[self._search]),
                ft.Divider(height=1),
                self._list_column,
            ],
        )

    def _on_search_change(self, e: ft.ControlEvent) -> None:
        self._apply_filter(self._search.value or "")

    def _apply_filter(self, query: str) -> None:
        q = query or ""
        if not q.strip():
            self._filtered = list(self._all_faqs)
        else:
            scored = []
            for item in self._all_faqs:
                text = f"{item.question}\n{item.answer}"
                scored.append((_cheap_fuzzy_score(q, text), item))
            scored.sort(key=lambda x: x[0], reverse=True)
            # Keep only reasonably relevant results
            self._filtered = [it for score, it in scored if score >= 0.2]

        self._rebuild_list()
        self.page.update()

    def _rebuild_list(self) -> None:
        self._list_column.controls.clear()

        if not self._filtered:
            self._list_column.controls.append(
                ft.Container(
                    padding=12,
                    content=ft.Text("No FAQs match your search."),
                )
            )
            return

        for item in self._filtered:
            self._list_column.controls.append(self._faq_card(item))

    def _faq_card(self, item: FaqItem) -> ft.Control:
        answer = ft.Text(item.answer, selectable=True)

        return ft.Card(
            content=ft.Container(
                padding=12,
                bgcolor=BRAND_LIGHT_GREY,
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Container(
                            content=ft.ExpansionTile(
                                title=ft.Text(
                                    item.question,
                                    size=16,
                                    weight=ft.FontWeight.BOLD, 
                                    selectable=True, 
                                    color=PRIMARY_GREEN
                                ),
                                subtitle=ft.Text("Show answer", color=PRIMARY_GREEN),
                                dense=True,
                                controls=[
                                    ft.Text(
                                        item.answer,
                                        text_align=ft.TextAlign.LEFT, 
                                        selectable=True, 
                                        color=BRAND_DARK_GREY
                                    ),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.END,
                                        controls=[
                                            ft.ElevatedButton(
                                                text="Open chat",
                                                color=BRAND_BACKGROUND,
                                                bgcolor=BRAND_ACCENT_BLUE,
                                                icon=ft.icons.CHAT_BUBBLE_OUTLINE,
                                                on_click=lambda e, it=item: self._on_open_chat_from_faq(it),
                                            )
                                        ],
                                    )
                                ]
                            )
                        )
                    ],
                ),
            )
        )