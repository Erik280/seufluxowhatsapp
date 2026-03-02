"""
Chat List - Lista de Conversas (Painel Esquerdo Interno)
"""
import flet as ft
from datetime import datetime
from frontend.theme import Colors, Typography, Sizes
from frontend.state import state
from frontend.api_client import api


def _format_time(timestamp_str: str) -> str:
    """Formata o timestamp para exibição: se hoje mostra hora, senão a data."""
    if not timestamp_str:
        return ""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        now = datetime.now(dt.tzinfo)
        if dt.date() == now.date():
            return dt.strftime("%H:%M")
        elif (now - dt).days < 7:
            days = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
            return days[dt.weekday()]
        else:
            return dt.strftime("%d/%m")
    except Exception:
        return ""


def _get_status_color(status: str) -> str:
    mapping = {
        "bot": Colors.STATUS_BOT,
        "human": Colors.STATUS_HUMAN,
        "paused": Colors.STATUS_PAUSED,
    }
    return mapping.get(status, Colors.TEXT_MUTED)


def _get_status_label(status: str) -> str:
    mapping = {"bot": "BOT", "human": "HUMANO", "paused": "PAUSADO"}
    return mapping.get(status, "?")


def _build_contact_item(contact: dict, on_select) -> ft.Container:
    name = contact.get("full_name") or contact.get("phone", "Contato")
    phone = contact.get("phone", "")
    status = contact.get("chat_status", "bot")
    last_time = _format_time(contact.get("last_interaction", ""))
    unread = contact.get("unread_count", 0)
    tags = [ct.get("tags", {}) for ct in contact.get("contact_tags", []) if ct.get("tags")]
    is_selected = state.selected_contact_id == contact.get("id")

    # Avatar com iniciais
    initials = (name[0]).upper() if name else "?"
    avatar = ft.Container(
        content=ft.Stack([
            ft.Container(
                content=ft.Text(initials, size=Typography.SIZE_MD, weight=ft.FontWeight.BOLD, color=Colors.TEXT_ON_ACCENT),
                width=Sizes.AVATAR_MD,
                height=Sizes.AVATAR_MD,
                border_radius=Sizes.AVATAR_MD // 2,
                alignment=ft.alignment.center,
                gradient=ft.LinearGradient(
                    colors=[Colors.NEON_CYAN + "AA", Colors.NEON_GREEN + "AA"],
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                ),
            ),
            # Bolinha de status
            ft.Container(
                width=12,
                height=12,
                border_radius=6,
                bgcolor=_get_status_color(status),
                border=ft.border.all(2, Colors.DARK_BG_SURFACE),
                right=0,
                bottom=0,
            ),
        ]),
        width=Sizes.AVATAR_MD,
        height=Sizes.AVATAR_MD,
    )

    # Badge de não lidas
    unread_badge = ft.Container(
        content=ft.Text(str(unread), size=10, color=Colors.TEXT_ON_ACCENT, weight=ft.FontWeight.BOLD),
        width=18,
        height=18,
        border_radius=9,
        bgcolor=Colors.NEON_CYAN,
        alignment=ft.alignment.center,
        visible=unread > 0,
    )

    # Tags chips
    tag_chips = ft.Row(
        controls=[
            ft.Container(
                content=ft.Text(t.get("name", ""), size=9, color=Colors.TEXT_ON_ACCENT),
                bgcolor=t.get("color", "#3498db") + "CC",
                border_radius=4,
                padding=ft.padding.symmetric(horizontal=5, vertical=1),
            )
            for t in tags[:3]
        ],
        spacing=3,
        wrap=True,
    )

    return ft.Container(
        content=ft.Row(
            controls=[
                avatar,
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(
                                    name,
                                    size=Typography.SIZE_MD,
                                    weight=ft.FontWeight.W_600 if unread > 0 else ft.FontWeight.W_400,
                                    color=Colors.TEXT_PRIMARY,
                                    expand=True,
                                    no_wrap=True,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Text(last_time, size=Typography.SIZE_XS, color=Colors.TEXT_MUTED),
                            ],
                            spacing=4,
                        ),
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Text(
                                        _get_status_label(status),
                                        size=9,
                                        color=_get_status_color(status),
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    border=ft.border.all(1, _get_status_color(status) + "60"),
                                    border_radius=4,
                                    padding=ft.padding.symmetric(horizontal=5, vertical=1),
                                ),
                                ft.Text(
                                    phone,
                                    size=Typography.SIZE_XS,
                                    color=Colors.TEXT_MUTED,
                                    expand=True,
                                    no_wrap=True,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                unread_badge,
                            ],
                            spacing=6,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        tag_chips if tags else ft.Container(height=0),
                    ],
                    spacing=4,
                    expand=True,
                ),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
        bgcolor=Colors.DARK_BG_ELEVATED if is_selected else ft.Colors.TRANSPARENT,
        border=ft.border.only(left=ft.BorderSide(3, Colors.NEON_CYAN)) if is_selected else None,
        border_radius=Sizes.BORDER_RADIUS_SM,
        on_click=lambda e: on_select(contact),
        on_hover=lambda e: _on_hover(e, is_selected),
    )


def _on_hover(e: ft.ControlEvent, is_selected: bool):
    if not is_selected:
        e.control.bgcolor = Colors.DARK_BG_HOVER if e.data == "true" else ft.Colors.TRANSPARENT
        e.control.update()


def build_chat_list(page: ft.Page, on_contact_select) -> ft.Column:
    """Constrói o painel da lista de conversas."""
    search_value = [""]
    filter_status = [""]

    search_field = ft.TextField(
        hint_text="Buscar conversa...",
        prefix_icon=ft.Icons.SEARCH,
        bgcolor=Colors.DARK_BG_ELEVATED,
        border_color=Colors.DARK_BG_ELEVATED,
        focused_border_color=Colors.NEON_CYAN,
        text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY, size=Typography.SIZE_SM),
        hint_style=ft.TextStyle(color=Colors.TEXT_MUTED, size=Typography.SIZE_SM),
        cursor_color=Colors.NEON_CYAN,
        height=40,
        border_radius=Sizes.BORDER_RADIUS_SM,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
        on_change=lambda e: _on_search(e.data),
    )

    contacts_list = ft.ListView(
        spacing=2,
        expand=True,
    )

    loading_ring = ft.ProgressRing(color=Colors.NEON_CYAN, width=24, height=24, stroke_width=2)
    loading_container = ft.Container(
        content=loading_ring,
        alignment=ft.alignment.center,
        visible=False,
        padding=20,
    )

    empty_state = ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE, color=Colors.TEXT_MUTED, size=48),
                ft.Text("Nenhuma conversa", color=Colors.TEXT_MUTED, size=Typography.SIZE_MD),
                ft.Text("As conversas aparecem aqui", color=Colors.TEXT_MUTED, size=Typography.SIZE_SM),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        ),
        alignment=ft.alignment.center,
        padding=40,
        visible=False,
    )

    def _render_contacts(contacts: list):
        filtered = contacts
        if search_value[0]:
            q = search_value[0].lower()
            filtered = [c for c in contacts if q in (c.get("full_name") or "").lower() or q in (c.get("phone") or "").lower()]
        if filter_status[0]:
            filtered = [c for c in filtered if c.get("chat_status") == filter_status[0]]

        contacts_list.controls.clear()
        if not filtered:
            empty_state.visible = True
        else:
            empty_state.visible = False
            for contact in filtered:
                contacts_list.controls.append(_build_contact_item(contact, on_contact_select))
        try:
            page.update()
        except Exception:
            pass

    def _on_search(value: str):
        search_value[0] = value
        _render_contacts(state.contacts)

    def load_contacts():
        loading_container.visible = True
        try:
            page.update()
        except Exception:
            pass
        try:
            contacts = api.get_contacts(limit=100)
            state.update_contacts(contacts)
            _render_contacts(contacts)
        except Exception as e:
            print(f"[ChatList] Erro ao carregar contatos: {e}")
        finally:
            loading_container.visible = False
            try:
                page.update()
            except Exception:
                pass

    # Escuta atualizações do estado
    def _on_state_change(section: str, data=None):
        if section in ("contacts", "new_message"):
            _render_contacts(state.contacts)

    state.subscribe(_on_state_change)

    # Status filter chips
    status_filters = ft.Row(
        controls=[
            _build_filter_chip("Todos", "", filter_status, _render_contacts),
            _build_filter_chip("Bot", "bot", filter_status, _render_contacts),
            _build_filter_chip("Humano", "human", filter_status, _render_contacts),
            _build_filter_chip("Pausado", "paused", filter_status, _render_contacts),
        ],
        spacing=6,
        scroll=ft.ScrollMode.AUTO,
    )

    # Carrega contatos ao iniciar
    import threading
    threading.Thread(target=load_contacts, daemon=True).start()

    return ft.Column(
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text("Conversas", size=Typography.SIZE_LG, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY, expand=True),
                                ft.IconButton(
                                    icon=ft.Icons.REFRESH,
                                    icon_color=Colors.TEXT_SECONDARY,
                                    icon_size=18,
                                    on_click=lambda e: threading.Thread(target=load_contacts, daemon=True).start(),
                                    tooltip="Atualizar conversas",
                                ),
                            ],
                        ),
                        search_field,
                        status_filters,
                    ],
                    spacing=8,
                ),
                padding=ft.padding.all(12),
            ),
            ft.Divider(color=Colors.DARK_BG_ELEVATED, height=1),
            loading_container,
            empty_state,
            contacts_list,
        ],
        expand=True,
        spacing=0,
    )


def _build_filter_chip(label: str, value: str, filter_status: list, render_fn) -> ft.Container:
    def on_click(e):
        filter_status[0] = value
        render_fn([])  # Trigger re-render com lista atual
    
    is_active = filter_status[0] == value
    return ft.Container(
        content=ft.Text(label, size=Typography.SIZE_XS, color=Colors.NEON_CYAN if is_active else Colors.TEXT_SECONDARY),
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
        border_radius=12,
        bgcolor=Colors.DARK_BG_ELEVATED if is_active else ft.Colors.TRANSPARENT,
        border=ft.border.all(1, Colors.NEON_CYAN if is_active else Colors.DARK_BG_ELEVATED),
        on_click=on_click,
    )
