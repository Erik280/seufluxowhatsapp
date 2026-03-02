"""
Painel CRM Direito - Dados do cliente e tags
"""
import flet as ft
import threading
from frontend.theme import Colors, Typography, Sizes, neon_button_style
from frontend.state import state
from frontend.api_client import api, APIError


def build_crm_panel(page: ft.Page) -> ft.Container:
    """Constrói o painel CRM lateral direito."""

    name_field = ft.TextField(
        label="Nome completo",
        bgcolor=Colors.DARK_BG_ELEVATED,
        border_color=Colors.DARK_BG_ELEVATED,
        focused_border_color=Colors.NEON_CYAN,
        label_style=ft.TextStyle(color=Colors.TEXT_SECONDARY, size=Typography.SIZE_SM),
        text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY),
        cursor_color=Colors.NEON_CYAN,
        height=44,
        border_radius=Sizes.BORDER_RADIUS_SM,
    )

    email_field = ft.TextField(
        label="E-mail",
        keyboard_type=ft.KeyboardType.EMAIL,
        bgcolor=Colors.DARK_BG_ELEVATED,
        border_color=Colors.DARK_BG_ELEVATED,
        focused_border_color=Colors.NEON_CYAN,
        label_style=ft.TextStyle(color=Colors.TEXT_SECONDARY, size=Typography.SIZE_SM),
        text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY),
        cursor_color=Colors.NEON_CYAN,
        height=44,
        border_radius=Sizes.BORDER_RADIUS_SM,
    )

    address_field = ft.TextField(
        label="Endereço",
        multiline=True,
        min_lines=2,
        max_lines=3,
        bgcolor=Colors.DARK_BG_ELEVATED,
        border_color=Colors.DARK_BG_ELEVATED,
        focused_border_color=Colors.NEON_CYAN,
        label_style=ft.TextStyle(color=Colors.TEXT_SECONDARY, size=Typography.SIZE_SM),
        text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY),
        cursor_color=Colors.NEON_CYAN,
        border_radius=Sizes.BORDER_RADIUS_SM,
    )

    notes_field = ft.TextField(
        label="Notas internas",
        multiline=True,
        min_lines=3,
        max_lines=5,
        bgcolor=Colors.DARK_BG_ELEVATED,
        border_color=Colors.DARK_BG_ELEVATED,
        focused_border_color=Colors.NEON_CYAN,
        label_style=ft.TextStyle(color=Colors.TEXT_SECONDARY, size=Typography.SIZE_SM),
        text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY),
        cursor_color=Colors.NEON_CYAN,
        border_radius=Sizes.BORDER_RADIUS_SM,
    )

    save_btn = ft.ElevatedButton(
        text="Salvar",
        icon=ft.Icons.SAVE,
        style=neon_button_style(),
        height=36,
        on_click=lambda e: save_contact(),
    )

    status_text = ft.Text("", size=Typography.SIZE_SM, color=Colors.SUCCESS, visible=False)

    # Tags section
    available_tags_row = ft.Wrap(spacing=6, run_spacing=6)
    selected_tag_ids: list = []

    def load_tags():
        try:
            tags = api.get_tags()
            state.tags = tags
            _render_tags(tags)
        except Exception:
            pass

    def _render_tags(tags: list):
        available_tags_row.controls.clear()
        for tag in tags:
            tag_id = tag.get("id")
            is_selected = tag_id in selected_tag_ids
            available_tags_row.controls.append(
                _build_tag_chip(tag, is_selected, lambda tid=tag_id: _toggle_tag(tid))
            )
        try:
            page.update()
        except Exception:
            pass

    def _toggle_tag(tag_id: str):
        if tag_id in selected_tag_ids:
            selected_tag_ids.remove(tag_id)
        else:
            selected_tag_ids.append(tag_id)
        _render_tags(state.tags)

    def load_contact_data(contact: dict):
        name_field.value = contact.get("full_name") or ""
        email_field.value = contact.get("email") or ""
        addr = contact.get("address") or {}
        address_field.value = addr.get("full", "") if isinstance(addr, dict) else str(addr)
        notes_field.value = contact.get("notes") or ""

        # Tags selecionadas
        selected_tag_ids.clear()
        for ct in contact.get("contact_tags", []):
            tid = ct.get("tag_id")
            if tid:
                selected_tag_ids.append(tid)

        _render_tags(state.tags)
        try:
            page.update()
        except Exception:
            pass

    def save_contact():
        if not state.selected_contact_id:
            return

        def _save():
            try:
                # Atualiza dados do contato
                api.update_contact(state.selected_contact_id, {
                    "full_name": name_field.value.strip() or None,
                    "email": email_field.value.strip() or None,
                    "address": {"full": address_field.value.strip()} if address_field.value.strip() else {},
                    "notes": notes_field.value.strip() or None,
                })

                # Atualiza tags
                api.set_contact_tags(state.selected_contact_id, selected_tag_ids)

                status_text.value = "✓ Salvo com sucesso!"
                status_text.color = Colors.SUCCESS
                status_text.visible = True
                try:
                    page.update()
                except Exception:
                    pass

                # Recarrega contatos para atualizar a lista
                threading.Timer(2, lambda: _hide_status()).start()

            except APIError as e:
                status_text.value = f"✗ Erro: {e.message}"
                status_text.color = Colors.ERROR
                status_text.visible = True
                try:
                    page.update()
                except Exception:
                    pass

        threading.Thread(target=_save, daemon=True).start()

    def _hide_status():
        status_text.visible = False
        try:
            page.update()
        except Exception:
            pass

    # Info do contato (somente leitura)
    phone_info = ft.Container(visible=False)
    status_badge = ft.Container(visible=False)

    def _update_info(contact: dict):
        phone = contact.get("phone", "")
        status = contact.get("chat_status", "bot")
        status_colors = {"bot": Colors.STATUS_BOT, "human": Colors.STATUS_HUMAN, "paused": Colors.STATUS_PAUSED}
        status_labels = {"bot": "🤖 BOT", "human": "👤 HUMANO", "paused": "⏸ PAUSADO"}

        phone_info.content = ft.Row(
            controls=[
                ft.Icon(ft.Icons.PHONE, color=Colors.TEXT_MUTED, size=14),
                ft.Text(phone, size=Typography.SIZE_SM, color=Colors.TEXT_SECONDARY, selectable=True),
            ],
            spacing=6,
        )
        phone_info.visible = True

        status_badge.content = ft.Container(
            content=ft.Text(status_labels.get(status, "?"), size=10, color=status_colors.get(status, Colors.TEXT_MUTED)),
            border=ft.border.all(1, status_colors.get(status, Colors.TEXT_MUTED) + "60"),
            border_radius=4,
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
        )
        status_badge.visible = True

        load_contact_data(contact)

    # Escuta mudanças de estado
    def _on_state_change(section: str, data=None):
        if section == "contact_selected" and data:
            _update_info(data)
            if not state.tags:
                threading.Thread(target=load_tags, daemon=True).start()

    state.subscribe(_on_state_change)

    # Carrega tags ao montar
    threading.Thread(target=load_tags, daemon=True).start()

    # Nova tag
    new_tag_name = ft.TextField(
        hint_text="Nova tag...",
        bgcolor=Colors.DARK_BG_ELEVATED,
        border_color=Colors.DARK_BG_ELEVATED,
        focused_border_color=Colors.NEON_CYAN,
        text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY, size=Typography.SIZE_SM),
        cursor_color=Colors.NEON_CYAN,
        height=36,
        border_radius=Sizes.BORDER_RADIUS_SM,
        expand=True,
    )
    new_tag_color = ft.Dropdown(
        options=[
            ft.dropdown.Option("#00E5CC", "Ciano"),
            ft.dropdown.Option("#00FF88", "Verde"),
            ft.dropdown.Option("#FFD700", "Ouro"),
            ft.dropdown.Option("#FF4466", "Vermelho"),
            ft.dropdown.Option("#FFA500", "Laranja"),
            ft.dropdown.Option("#9B59B6", "Roxo"),
            ft.dropdown.Option("#3498DB", "Azul"),
        ],
        value="#00E5CC",
        bgcolor=Colors.DARK_BG_ELEVATED,
        border_color=Colors.DARK_BG_ELEVATED,
        focused_border_color=Colors.NEON_CYAN,
        text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY, size=Typography.SIZE_SM),
        height=36,
        width=80,
    )

    def create_tag():
        name = new_tag_name.value.strip()
        if not name:
            return
        def _create():
            try:
                tag = api.create_tag(name, new_tag_color.value or "#00E5CC")
                state.tags.append(tag)
                new_tag_name.value = ""
                _render_tags(state.tags)
            except Exception:
                pass
        threading.Thread(target=_create, daemon=True).start()

    return ft.Container(
        content=ft.Column(
            controls=[
                # Header
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text("CRM do Contato", size=Typography.SIZE_MD, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY, expand=True),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                icon_color=Colors.TEXT_SECONDARY,
                                icon_size=18,
                                on_click=lambda e: state.toggle_crm(),
                                tooltip="Fechar",
                            ),
                        ],
                    ),
                    padding=ft.padding.all(12),
                ),
                ft.Divider(color=Colors.DARK_BG_ELEVATED, height=1),

                # Scroll content
                ft.Column(
                    controls=[
                        ft.Container(height=8),
                        phone_info,
                        status_badge,
                        ft.Container(height=8),
                        ft.Text("DADOS DO CLIENTE", size=9, color=Colors.TEXT_MUTED, letter_spacing=1.5),
                        ft.Container(height=4),
                        name_field,
                        email_field,
                        address_field,
                        notes_field,
                        status_text,
                        save_btn,

                        ft.Container(height=16),
                        ft.Divider(color=Colors.DARK_BG_ELEVATED, height=1),
                        ft.Container(height=8),

                        ft.Text("TAGS", size=9, color=Colors.TEXT_MUTED, letter_spacing=1.5),
                        ft.Container(height=4),
                        available_tags_row,
                        ft.Container(height=8),

                        ft.Text("NOVA TAG", size=9, color=Colors.TEXT_MUTED, letter_spacing=1.5),
                        ft.Container(height=4),
                        ft.Row(
                            controls=[
                                new_tag_name,
                                new_tag_color,
                                ft.IconButton(
                                    icon=ft.Icons.ADD,
                                    icon_color=Colors.NEON_CYAN,
                                    icon_size=18,
                                    on_click=lambda e: create_tag(),
                                    tooltip="Criar tag",
                                ),
                            ],
                            spacing=6,
                        ),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                    spacing=8,
                ),
            ],
            expand=True,
            spacing=0,
        ),
        width=Sizes.CRM_PANEL_WIDTH,
        bgcolor=Colors.DARK_BG_SURFACE,
        border=ft.border.only(left=ft.BorderSide(1, Colors.DARK_BG_ELEVATED)),
        padding=ft.padding.symmetric(horizontal=12),
    )


def _build_tag_chip(tag: dict, is_selected: bool, on_click) -> ft.Container:
    color = tag.get("color", "#3498db")
    name = tag.get("name", "")
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(width=8, height=8, border_radius=4, bgcolor=color),
                ft.Text(name, size=Typography.SIZE_XS, color=Colors.TEXT_PRIMARY),
            ] + ([ft.Icon(ft.Icons.CHECK, size=12, color=color)] if is_selected else []),
            spacing=4,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(horizontal=10, vertical=5),
        border_radius=12,
        bgcolor=color + "25" if is_selected else Colors.DARK_BG_ELEVATED,
        border=ft.border.all(1, color if is_selected else Colors.DARK_BG_ELEVATED),
        on_click=lambda e: on_click(),
    )
