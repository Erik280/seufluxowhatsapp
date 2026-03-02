"""
Bolhas de Mensagem - Componente reutilizável
"""
import flet as ft
from datetime import datetime
from frontend.theme import Colors, Typography, Sizes


def _format_msg_time(timestamp_str: str) -> str:
    if not timestamp_str:
        return ""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        return dt.strftime("%H:%M")
    except Exception:
        return ""


def build_message_bubble(message: dict) -> ft.Container:
    """Constrói uma bolha de mensagem."""
    direction = message.get("direction", "in")
    is_outgoing = direction == "out"
    msg_type = message.get("message_type", "text")
    content = message.get("content", "")
    media_url = message.get("media_url", "")
    timestamp = _format_msg_time(message.get("timestamp", ""))
    status = message.get("status", "")

    # Conteúdo da bolha baseado no tipo
    bubble_content = _build_content(msg_type, content, media_url, is_outgoing)

    # Timestamp e status
    status_icon = None
    if is_outgoing:
        status_icons = {
            "sent": ft.Icons.CHECK,
            "delivered": ft.Icons.DONE_ALL,
            "read": ft.Icons.DONE_ALL,
            "failed": ft.Icons.ERROR_OUTLINE,
        }
        icon = status_icons.get(status, ft.Icons.CHECK)
        color = Colors.NEON_CYAN if status == "read" else Colors.TEXT_ON_ACCENT + "80"
        if status == "failed":
            color = Colors.ERROR
        status_icon = ft.Icon(icon, size=12, color=color)

    timestamp_row = ft.Row(
        controls=[
            ft.Text(timestamp, size=9, color=(Colors.TEXT_ON_ACCENT + "80") if is_outgoing else Colors.TEXT_MUTED),
        ] + ([status_icon] if status_icon else []),
        spacing=3,
        alignment=ft.MainAxisAlignment.END,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    bubble = ft.Container(
        content=ft.Column(
            controls=[bubble_content, timestamp_row],
            spacing=4,
        ),
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
        border_radius=ft.border_radius.only(
            top_left=Sizes.BORDER_RADIUS,
            top_right=Sizes.BORDER_RADIUS,
            bottom_left=0 if not is_outgoing else Sizes.BORDER_RADIUS,
            bottom_right=Sizes.BORDER_RADIUS if not is_outgoing else 0,
        ),
        bgcolor=Colors.BUBBLE_OUT if is_outgoing else Colors.BUBBLE_IN,
        border=ft.border.all(1, Colors.NEON_CYAN + "20") if not is_outgoing else None,
        shadow=ft.BoxShadow(
            blur_radius=10,
            color="#00000040",
            offset=ft.Offset(0, 2),
        ),
        max_width=460,
    )

    return ft.Container(
        content=ft.Row(
            controls=[bubble],
            alignment=ft.MainAxisAlignment.END if is_outgoing else ft.MainAxisAlignment.START,
        ),
        padding=ft.padding.symmetric(horizontal=16, vertical=2),
    )


def _build_content(msg_type: str, content: str, media_url: str, is_outgoing: bool) -> ft.Control:
    text_color = Colors.BUBBLE_OUT_TEXT if is_outgoing else Colors.TEXT_PRIMARY

    if msg_type == "text":
        return ft.Text(
            content or "",
            size=Typography.SIZE_MD,
            color=text_color,
            selectable=True,
        )

    elif msg_type == "image" and media_url:
        controls = [
            ft.Image(
                src=media_url,
                width=280,
                height=200,
                fit=ft.ImageFit.COVER,
                border_radius=Sizes.BORDER_RADIUS_SM,
                error_content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED, color=Colors.TEXT_MUTED, size=32),
                        ft.Text("Imagem indisponível", color=Colors.TEXT_MUTED, size=10),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    width=280, height=120,
                    alignment=ft.alignment.center,
                ),
            ),
        ]
        if content:
            controls.append(ft.Text(content, size=Typography.SIZE_SM, color=text_color))
        return ft.Column(controls=controls, spacing=4)

    elif msg_type == "audio":
        return ft.Row(
            controls=[
                ft.Icon(ft.Icons.MIC, color=text_color, size=20),
                ft.Text("Mensagem de voz", size=Typography.SIZE_SM, color=text_color, italic=True),
            ],
            spacing=8,
        )

    elif msg_type == "video" and media_url:
        controls = [
            ft.Container(
                content=ft.Stack([
                    ft.Container(
                        width=280, height=160,
                        bgcolor=Colors.DARK_BG_DEEP,
                        border_radius=Sizes.BORDER_RADIUS_SM,
                    ),
                    ft.Container(
                        content=ft.Icon(ft.Icons.PLAY_CIRCLE_FILLED, color=Colors.NEON_CYAN, size=48),
                        alignment=ft.alignment.center,
                    ),
                ]),
                width=280, height=160,
            ),
        ]
        if content:
            controls.append(ft.Text(content, size=Typography.SIZE_SM, color=text_color))
        return ft.Column(controls=controls, spacing=4)

    elif msg_type == "document":
        return ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(ft.Icons.INSERT_DRIVE_FILE, color=text_color, size=28),
                    width=44,
                    height=44,
                    border_radius=8,
                    bgcolor=Colors.DARK_BG_ELEVATED if not is_outgoing else Colors.TEXT_ON_ACCENT + "20",
                    alignment=ft.alignment.center,
                ),
                ft.Column(
                    controls=[
                        ft.Text(content or "Documento", size=Typography.SIZE_SM, weight=ft.FontWeight.W_500, color=text_color),
                        ft.Text("Toque para baixar", size=Typography.SIZE_XS, color=(text_color + "80")),
                    ],
                    spacing=2,
                    expand=True,
                ),
            ],
            spacing=10,
        )

    elif msg_type == "sticker":
        return ft.Text("😊 [Sticker]", size=Typography.SIZE_XL)

    return ft.Text(content or "", size=Typography.SIZE_MD, color=text_color)
