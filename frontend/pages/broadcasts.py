"""
Módulo de Broadcasts - Agendamento de mensagens em massa
"""
import flet as ft
import threading
from datetime import datetime, timedelta
from frontend.theme import Colors, Typography, Sizes, neon_button_style, ghost_button_style
from frontend.state import state
from frontend.api_client import api, APIError
from frontend.components.sidebar import build_sidebar


def _format_dt(dt_str: str) -> str:
    if not dt_str:
        return "-"
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return dt_str


def _status_color(status: str) -> str:
    mapping = {
        "pending": Colors.WARNING,
        "sending": Colors.INFO,
        "completed": Colors.SUCCESS,
        "failed": Colors.ERROR,
        "cancelled": Colors.TEXT_MUTED,
    }
    return mapping.get(status, Colors.TEXT_MUTED)


def _status_label(status: str) -> str:
    mapping = {
        "pending": "⏳ AGUARDANDO",
        "sending": "📤 ENVIANDO",
        "completed": "✓ CONCLUÍDO",
        "failed": "✗ FALHOU",
        "cancelled": "✘ CANCELADO",
    }
    return mapping.get(status, status.upper())


def BroadcastsPage(page: ft.Page):
    """Página de gerenciamento de broadcasts."""

    broadcasts_list = ft.ListView(spacing=8, expand=True)
    loading = ft.ProgressRing(color=Colors.NEON_CYAN, width=32, height=32, stroke_width=3)
    loading_container = ft.Container(content=loading, alignment=ft.alignment.center, visible=False, expand=True)

    # Form de criação
    title_field = ft.TextField(
        label="Título do broadcast",
        bgcolor=Colors.DARK_BG_ELEVATED,
        border_color=Colors.DARK_BG_ELEVATED,
        focused_border_color=Colors.NEON_CYAN,
        label_style=ft.TextStyle(color=Colors.TEXT_SECONDARY, size=Typography.SIZE_SM),
        text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY),
        cursor_color=Colors.NEON_CYAN,
        border_radius=Sizes.BORDER_RADIUS_SM,
    )

    content_field = ft.TextField(
        label="Mensagem",
        multiline=True,
        min_lines=4,
        max_lines=8,
        bgcolor=Colors.DARK_BG_ELEVATED,
        border_color=Colors.DARK_BG_ELEVATED,
        focused_border_color=Colors.NEON_CYAN,
        label_style=ft.TextStyle(color=Colors.TEXT_SECONDARY, size=Typography.SIZE_SM),
        text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY),
        cursor_color=Colors.NEON_CYAN,
        border_radius=Sizes.BORDER_RADIUS_SM,
    )

    scheduled_date = ft.TextField(
        label="Data de envio (AAAA-MM-DD HH:MM)",
        hint_text=f"{(datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')}",
        bgcolor=Colors.DARK_BG_ELEVATED,
        border_color=Colors.DARK_BG_ELEVATED,
        focused_border_color=Colors.NEON_CYAN,
        label_style=ft.TextStyle(color=Colors.TEXT_SECONDARY, size=Typography.SIZE_SM),
        text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY),
        cursor_color=Colors.NEON_CYAN,
        border_radius=Sizes.BORDER_RADIUS_SM,
    )

    form_error = ft.Text("", color=Colors.ERROR, size=Typography.SIZE_SM, visible=False)
    form_success = ft.Text("", color=Colors.SUCCESS, size=Typography.SIZE_SM, visible=False)

    def load_broadcasts():
        loading_container.visible = True
        broadcasts_list.visible = False
        try:
            page.update()
        except Exception:
            pass
        try:
            data = api.get_broadcasts()
            _render_broadcasts(data)
        except Exception as e:
            print(f"[Broadcasts] Erro: {e}")
        finally:
            loading_container.visible = False
            broadcasts_list.visible = True
            try:
                page.update()
            except Exception:
                pass

    def _render_broadcasts(data: list):
        broadcasts_list.controls.clear()
        for b in data:
            broadcasts_list.controls.append(_build_broadcast_card(b))
        try:
            page.update()
        except Exception:
            pass

    def _build_broadcast_card(b: dict) -> ft.Container:
        status = b.get("status", "pending")
        color = _status_color(status)
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(b.get("title", "Sem título"), size=Typography.SIZE_MD, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY, expand=True),
                            ft.Container(
                                content=ft.Text(_status_label(status), size=9, color=color, weight=ft.FontWeight.BOLD),
                                border=ft.border.all(1, color + "60"),
                                border_radius=4,
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                            ),
                        ],
                    ),
                    ft.Text(b.get("content", "")[:120] + ("..." if len(b.get("content", "")) > 120 else ""), size=Typography.SIZE_SM, color=Colors.TEXT_SECONDARY),
                    ft.Row(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.SCHEDULE, color=Colors.TEXT_MUTED, size=13),
                                    ft.Text(_format_dt(b.get("scheduled_at", "")), size=Typography.SIZE_XS, color=Colors.TEXT_MUTED),
                                ],
                                spacing=4,
                            ),
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=Colors.SUCCESS, size=13),
                                    ft.Text(f"{b.get('sent_count', 0)} enviados", size=Typography.SIZE_XS, color=Colors.TEXT_MUTED),
                                ],
                                spacing=4,
                            ),
                            ft.Container(expand=True),
                            ft.TextButton(
                                text="Cancelar",
                                style=ft.ButtonStyle(color={ft.ControlState.DEFAULT: Colors.ERROR}),
                                on_click=lambda e, bid=b.get("id"): cancel_broadcast(bid),
                                visible=status == "pending",
                            ),
                        ],
                        spacing=16,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=8,
            ),
            padding=ft.padding.all(16),
            border_radius=Sizes.BORDER_RADIUS,
            bgcolor=Colors.DARK_BG_SURFACE,
            border=ft.border.all(1, color + "20"),
        )

    def cancel_broadcast(bid: str):
        def _cancel():
            try:
                api.cancel_broadcast(bid)
                load_broadcasts()
            except APIError as e:
                print(f"[Broadcasts] Erro ao cancelar: {e.message}")
        threading.Thread(target=_cancel, daemon=True).start()

    def create_broadcast():
        title = title_field.value.strip()
        content = content_field.value.strip()
        scheduled = scheduled_date.value.strip()

        if not title or not content:
            form_error.value = "Preencha título e mensagem"
            form_error.visible = True
            try:
                page.update()
            except Exception:
                pass
            return

        form_error.visible = False

        scheduled_at = None
        if scheduled:
            try:
                scheduled_at = datetime.strptime(scheduled, "%Y-%m-%d %H:%M").isoformat()
            except ValueError:
                form_error.value = "Formato de data inválido. Use AAAA-MM-DD HH:MM"
                form_error.visible = True
                try:
                    page.update()
                except Exception:
                    pass
                return

        def _create():
            try:
                api.create_broadcast({
                    "title": title,
                    "content": content,
                    "scheduled_at": scheduled_at,
                })
                title_field.value = ""
                content_field.value = ""
                scheduled_date.value = ""
                form_success.value = "✓ Broadcast criado e agendado!"
                form_success.visible = True
                try:
                    page.update()
                except Exception:
                    pass
                load_broadcasts()
                import time; time.sleep(3)
                form_success.visible = False
                try:
                    page.update()
                except Exception:
                    pass
            except APIError as e:
                form_error.value = f"Erro: {e.message}"
                form_error.visible = True
                try:
                    page.update()
                except Exception:
                    pass

        threading.Thread(target=_create, daemon=True).start()

    # Inicia carregamento
    threading.Thread(target=load_broadcasts, daemon=True).start()

    def on_navigate(page_id: str):
        if page_id != "broadcasts":
            page.go(f"/{page_id}")

    sidebar = build_sidebar(page, on_navigate)

    return ft.Row(
        controls=[
            sidebar,
            ft.Container(
                content=ft.Column(
                    controls=[
                        # Header
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Column(
                                        controls=[
                                            ft.Text("📢 Broadcasts", size=Typography.SIZE_2XL, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                                            ft.Text("Agendamento e envio em massa", size=Typography.SIZE_SM, color=Colors.TEXT_SECONDARY),
                                        ],
                                        spacing=4,
                                        expand=True,
                                    ),
                                    ft.ElevatedButton(
                                        text="Atualizar",
                                        icon=ft.Icons.REFRESH,
                                        style=ghost_button_style(),
                                        on_click=lambda e: threading.Thread(target=load_broadcasts, daemon=True).start(),
                                    ),
                                ],
                            ),
                            padding=ft.padding.all(24),
                        ),

                        # Conteúdo em 2 colunas
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    # Lista de broadcasts (esquerda)
                                    ft.Column(
                                        controls=[
                                            ft.Text("Broadcasts Agendados", size=Typography.SIZE_MD, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                                            ft.Container(height=8),
                                            loading_container,
                                            broadcasts_list,
                                        ],
                                        expand=True,
                                        spacing=0,
                                    ),

                                    ft.Container(width=24),

                                    # Formulário de criação (direita)
                                    ft.Container(
                                        content=ft.Column(
                                            controls=[
                                                ft.Text("➕ Novo Broadcast", size=Typography.SIZE_MD, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                                                ft.Container(height=8),
                                                title_field,
                                                content_field,
                                                scheduled_date,
                                                ft.Text("💡 Deixe a data em branco para enviar imediatamente.", size=Typography.SIZE_XS, color=Colors.TEXT_MUTED),
                                                form_error,
                                                form_success,
                                                ft.ElevatedButton(
                                                    text="Agendar Broadcast",
                                                    icon=ft.Icons.SCHEDULE_SEND,
                                                    style=neon_button_style(),
                                                    on_click=lambda e: create_broadcast(),
                                                ),
                                            ],
                                            spacing=12,
                                        ),
                                        width=380,
                                        padding=ft.padding.all(20),
                                        bgcolor=Colors.DARK_BG_SURFACE,
                                        border_radius=Sizes.BORDER_RADIUS,
                                        border=ft.border.all(1, Colors.NEON_CYAN + "20"),
                                    ),
                                ],
                                expand=True,
                                vertical_alignment=ft.CrossAxisAlignment.START,
                            ),
                            expand=True,
                            padding=ft.padding.symmetric(horizontal=24),
                        ),
                    ],
                    expand=True,
                    spacing=0,
                ),
                expand=True,
                bgcolor=Colors.DARK_BG_MAIN,
            ),
        ],
        expand=True,
        spacing=0,
    )
