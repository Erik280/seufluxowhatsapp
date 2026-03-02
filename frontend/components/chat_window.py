"""
Janela de Chat Central - Área de mensagens
"""
import flet as ft
import threading
from frontend.theme import Colors, Typography, Sizes, neon_button_style, ghost_button_style
from frontend.state import state
from frontend.api_client import api, APIError
from frontend.components.message_bubble import build_message_bubble


def build_chat_window(page: ft.Page) -> ft.Container:
    """Constrói a área central de chat."""

    messages_list = ft.ListView(
        spacing=2,
        expand=True,
        auto_scroll=True,
        padding=ft.padding.symmetric(vertical=8),
    )

    input_field = ft.TextField(
        hint_text="Digite uma mensagem...",
        expand=True,
        multiline=True,
        min_lines=1,
        max_lines=4,
        shift_enter=True,
        bgcolor=Colors.DARK_BG_ELEVATED,
        border_color=Colors.DARK_BG_ELEVATED,
        focused_border_color=Colors.NEON_CYAN,
        text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY, size=Typography.SIZE_MD),
        hint_style=ft.TextStyle(color=Colors.TEXT_MUTED),
        cursor_color=Colors.NEON_CYAN,
        border_radius=20,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=10),
    )

    send_btn = ft.IconButton(
        icon=ft.Icons.SEND_ROUNDED,
        icon_color=Colors.NEON_CYAN,
        icon_size=24,
        tooltip="Enviar mensagem",
        style=ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: Colors.NEON_CYAN + "20",
                ft.ControlState.HOVERED: Colors.NEON_CYAN + "40",
            },
            shape=ft.CircleBorder(),
        ),
        on_click=lambda e: send_message(),
    )

    # Cabeçalho do chat (nome do contato + status + ações)
    header_name = ft.Text("", size=Typography.SIZE_LG, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY)
    header_status = ft.Container(visible=False)
    takeover_btn = ft.ElevatedButton(
        text="Assumir Atendimento",
        icon=ft.Icons.SUPPORT_AGENT,
        style=neon_button_style(),
        height=36,
        visible=False,
        on_click=lambda e: do_takeover(),
    )
    release_btn = ft.OutlinedButton(
        text="Devolver ao Bot",
        icon=ft.Icons.SMART_TOY,
        style=ghost_button_style(),
        height=36,
        visible=False,
        on_click=lambda e: do_release(),
    )
    crm_btn = ft.IconButton(
        icon=ft.Icons.PERSON_OUTLINE,
        icon_color=Colors.TEXT_SECONDARY,
        icon_size=20,
        tooltip="Abrir CRM",
        on_click=lambda e: state.toggle_crm(),
    )

    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Column(
                    controls=[header_name, header_status],
                    spacing=4,
                    expand=True,
                ),
                takeover_btn,
                release_btn,
                crm_btn,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        padding=ft.padding.symmetric(horizontal=20, vertical=12),
        bgcolor=Colors.DARK_BG_SURFACE,
        border=ft.border.only(bottom=ft.BorderSide(1, Colors.DARK_BG_ELEVATED)),
    )

    # Tela de boas-vindas (quando nenhum contato selecionado)
    empty_chat = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE_ROUNDED, size=80, color=Colors.NEON_CYAN + "40"),
                    shadow=ft.BoxShadow(blur_radius=40, color=Colors.NEON_CYAN + "20"),
                ),
                ft.Text("WhatsApp Atendimento", size=Typography.SIZE_2XL, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                ft.Text("Selecione uma conversa para começar", size=Typography.SIZE_MD, color=Colors.TEXT_SECONDARY),
                ft.Container(
                    content=ft.Text(
                        "💡 Clique em uma conversa no painel esquerdo",
                        size=Typography.SIZE_SM,
                        color=Colors.TEXT_MUTED,
                    ),
                    padding=ft.padding.all(12),
                    border_radius=8,
                    bgcolor=Colors.DARK_BG_ELEVATED,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=16,
        ),
        expand=True,
        alignment=ft.alignment.center,
    )

    loading_messages = ft.Container(
        content=ft.Column(
            controls=[
                ft.ProgressRing(color=Colors.NEON_CYAN, width=32, height=32, stroke_width=3),
                ft.Text("Carregando mensagens...", color=Colors.TEXT_SECONDARY, size=Typography.SIZE_SM),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        ),
        expand=True,
        alignment=ft.alignment.center,
        visible=False,
    )

    def load_messages(contact_id: str):
        loading_messages.visible = True
        messages_list.visible = False
        try:
            page.update()
        except Exception:
            pass
        try:
            msgs = api.get_messages(contact_id)
            state.update_messages(msgs)
            _render_messages(msgs)
        except Exception as e:
            print(f"[ChatWindow] Erro ao carregar mensagens: {e}")
        finally:
            loading_messages.visible = False
            messages_list.visible = True
            try:
                page.update()
            except Exception:
                pass

    def _render_messages(messages: list):
        messages_list.controls.clear()
        for msg in messages:
            messages_list.controls.append(build_message_bubble(msg))
        try:
            page.update()
        except Exception:
            pass

    def _update_header(contact: dict):
        name = contact.get("full_name") or contact.get("phone", "Contato")
        status = contact.get("chat_status", "bot")

        header_name.value = name

        # Badge de status
        status_colors = {"bot": Colors.STATUS_BOT, "human": Colors.STATUS_HUMAN, "paused": Colors.STATUS_PAUSED}
        status_labels = {"bot": "🤖 BOT", "human": "👤 HUMANO", "paused": "⏸ PAUSADO"}
        header_status.content = ft.Container(
            content=ft.Text(status_labels.get(status, "?"), size=10, color=status_colors.get(status, Colors.TEXT_MUTED)),
            border=ft.border.all(1, status_colors.get(status, Colors.TEXT_MUTED) + "60"),
            border_radius=4,
            padding=ft.padding.symmetric(horizontal=6, vertical=2),
        )
        header_status.visible = True

        # Botões de ação
        takeover_btn.visible = status == "bot"
        release_btn.visible = status == "human"

        try:
            page.update()
        except Exception:
            pass

    def send_message():
        text = input_field.value.strip()
        if not text or not state.selected_contact_id:
            return

        contact = state.selected_contact
        if not contact:
            return

        input_field.value = ""
        try:
            page.update()
        except Exception:
            pass

        def _send():
            try:
                msg = api.send_message(state.selected_contact_id, text)
                state.add_message(msg)
                _render_messages(state.messages)
            except APIError as e:
                print(f"[ChatWindow] Erro ao enviar: {e.message}")

        threading.Thread(target=_send, daemon=True).start()

    def do_takeover():
        contact_id = state.selected_contact_id
        if not contact_id:
            return
        def _take():
            try:
                api.takeover(contact_id)
                # Atualiza o contato localmente
                if state.selected_contact:
                    state.selected_contact["chat_status"] = "human"
                    _update_header(state.selected_contact)
                    # Atualiza lista de contatos
                    for c in state.contacts:
                        if c.get("id") == contact_id:
                            c["chat_status"] = "human"
                    state.notify_all("contacts")
            except Exception as e:
                print(f"[ChatWindow] Takeover error: {e}")
        threading.Thread(target=_take, daemon=True).start()

    def do_release():
        contact_id = state.selected_contact_id
        if not contact_id:
            return
        def _release():
            try:
                api.release(contact_id)
                if state.selected_contact:
                    state.selected_contact["chat_status"] = "bot"
                    _update_header(state.selected_contact)
                    for c in state.contacts:
                        if c.get("id") == contact_id:
                            c["chat_status"] = "bot"
                    state.notify_all("contacts")
            except Exception as e:
                print(f"[ChatWindow] Release error: {e}")
        threading.Thread(target=_release, daemon=True).start()

    # Enter para enviar
    input_field.on_submit = lambda e: send_message()

    # Escuta mudanças de estado
    def _on_state_change(section: str, data=None):
        if section == "contact_selected" and data:
            _update_header(data)
            threading.Thread(target=lambda: load_messages(data.get("id")), daemon=True).start()
        elif section == "messages":
            _render_messages(state.messages)
        elif section == "new_message" and data:
            # Verifica se a nova mensagem é do contato selecionado
            if data.get("contact_id") == state.selected_contact_id:
                state.messages.append(data)
                messages_list.controls.append(build_message_bubble(data))
                try:
                    page.update()
                except Exception:
                    pass

    state.subscribe(_on_state_change)

    # Barra de input
    input_bar = ft.Container(
        content=ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ATTACH_FILE,
                    icon_color=Colors.TEXT_SECONDARY,
                    icon_size=22,
                    tooltip="Anexar arquivo",
                ),
                input_field,
                send_btn,
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.END,
        ),
        padding=ft.padding.symmetric(horizontal=16, vertical=10),
        bgcolor=Colors.DARK_BG_SURFACE,
        border=ft.border.only(top=ft.BorderSide(1, Colors.DARK_BG_ELEVATED)),
    )

    chat_area = ft.Column(
        controls=[
            header,
            ft.Stack(
                controls=[
                    empty_chat,
                    ft.Column(
                        controls=[loading_messages, messages_list],
                        expand=True,
                    ),
                ],
                expand=True,
            ),
            input_bar,
        ],
        expand=True,
        spacing=0,
    )

    def _on_contact_state(section: str, data=None):
        # Esconde empty state quando um contato é selecionado
        if section == "contact_selected":
            empty_chat.visible = False
            try:
                page.update()
            except Exception:
                pass

    state.subscribe(_on_contact_state)

    return ft.Container(
        content=chat_area,
        expand=True,
        bgcolor=Colors.DARK_BG_MAIN,
    )
