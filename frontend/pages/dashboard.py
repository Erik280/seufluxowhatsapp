"""
Dashboard Principal - Layout 3 colunas
"""
import flet as ft
from frontend.theme import Colors, Sizes
from frontend.state import state
from frontend.components.sidebar import build_sidebar
from frontend.components.chat_list import build_chat_list
from frontend.components.chat_window import build_chat_window
from frontend.components.crm_panel import build_crm_panel


def DashboardPage(page: ft.Page):
    """Constrói o layout principal do dashboard com 3 colunas."""

    def on_contact_select(contact: dict):
        state.select_contact(contact)

    def on_navigate(page_id: str):
        if page_id != "chats":
            page.go(f"/{page_id}")

    sidebar = build_sidebar(page, on_navigate)
    chat_list = build_chat_list(page, on_contact_select)
    chat_window = build_chat_window(page)
    crm = build_crm_panel(page)

    # CRM visível apenas quando state.crm_panel_visible
    crm_column = ft.AnimatedSwitcher(
        content=crm if state.crm_panel_visible else ft.Container(width=0),
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=200,
        switch_in_curve=ft.AnimationCurve.EASE_OUT,
        switch_out_curve=ft.AnimationCurve.EASE_IN,
    )

    def _on_state(section, data=None):
        if section == "crm":
            crm_column.content = crm if state.crm_panel_visible else ft.Container(width=0)
            try:
                page.update()
            except Exception:
                pass

    state.subscribe(_on_state)

    return ft.Row(
        controls=[
            sidebar,
            # Painel de lista de chats
            ft.Container(
                content=chat_list,
                width=Sizes.CHAT_LIST_WIDTH,
                bgcolor=Colors.DARK_BG_SURFACE,
                border=ft.border.only(right=ft.BorderSide(1, Colors.DARK_BG_ELEVATED)),
            ),
            # Área de chat central
            ft.Container(content=chat_window, expand=True),
            # CRM animado
            crm_column,
        ],
        expand=True,
        spacing=0,
    )
