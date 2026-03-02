"""
Sidebar - Menu Lateral Retrátil
"""
import flet as ft
from frontend.theme import Colors, Typography, Sizes
from frontend.state import state


MENU_ITEMS = [
    {"id": "dashboard", "icon": ft.Icons.DASHBOARD_OUTLINED, "icon_active": ft.Icons.DASHBOARD, "label": "Dashboard"},
    {"id": "chats", "icon": ft.Icons.CHAT_BUBBLE_OUTLINE, "icon_active": ft.Icons.CHAT_BUBBLE, "label": "Atendimento"},
    {"id": "broadcasts", "icon": ft.Icons.CAMPAIGN_OUTLINED, "icon_active": ft.Icons.CAMPAIGN, "label": "Broadcasts"},
    {"id": "settings", "icon": ft.Icons.SETTINGS_OUTLINED, "icon_active": ft.Icons.SETTINGS, "label": "Configurações"},
]

ADMIN_MENU_ITEMS = [
    {"id": "admin", "icon": ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED, "icon_active": ft.Icons.ADMIN_PANEL_SETTINGS, "label": "SuperAdmin"},
]


def build_sidebar(page: ft.Page, on_navigate=None) -> ft.Container:
    expanded = [state.sidebar_expanded]

    def toggle_expand(e=None):
        expanded[0] = not expanded[0]
        state.sidebar_expanded = expanded[0]
        _rebuild()

    def navigate(page_id: str):
        state.navigate(page_id)
        if on_navigate:
            on_navigate(page_id)

    def build_menu_item(item: dict) -> ft.Container:
        is_active = state.current_page == item["id"]
        icon = item["icon_active"] if is_active else item["icon"]

        icon_part = ft.Icon(
            icon,
            color=Colors.NEON_CYAN if is_active else Colors.TEXT_SECONDARY,
            size=22,
        )

        active_indicator = ft.Container(
            width=3,
            height=32,
            border_radius=2,
            bgcolor=Colors.NEON_CYAN,
            visible=is_active,
        )

        label = ft.Text(
            item["label"],
            size=Typography.SIZE_SM,
            weight=ft.FontWeight.W_500 if is_active else ft.FontWeight.W_400,
            color=Colors.NEON_CYAN if is_active else Colors.TEXT_SECONDARY,
            no_wrap=True,
        )

        return ft.Container(
            content=ft.Row(
                controls=[
                    active_indicator,
                    ft.Container(
                        content=ft.Row(
                            controls=[icon_part] + ([ft.Container(width=10), label] if expanded[0] else []),
                            spacing=0,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.symmetric(horizontal=12, vertical=10),
                    ),
                ],
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            height=48,
            border_radius=Sizes.BORDER_RADIUS_SM,
            bgcolor=Colors.DARK_BG_ELEVATED if is_active else ft.Colors.TRANSPARENT,
            on_hover=lambda e: _on_item_hover(e, is_active),
            on_click=lambda e: navigate(item["id"]),
            tooltip=item["label"] if not expanded[0] else None,
        )

    def _on_item_hover(e: ft.ControlEvent, is_active: bool):
        if not is_active:
            e.control.bgcolor = Colors.DARK_BG_HOVER if e.data == "true" else ft.Colors.TRANSPARENT
            e.control.update()

    def _build_user_avatar() -> ft.Container:
        user = state.user
        initials = ""
        if user:
            parts = (user.full_name or "?").split()
            initials = (parts[0][0] + (parts[1][0] if len(parts) > 1 else "")).upper()

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(initials, size=Typography.SIZE_SM, weight=ft.FontWeight.BOLD, color=Colors.TEXT_ON_ACCENT),
                        width=36,
                        height=36,
                        border_radius=18,
                        alignment=ft.alignment.center,
                        gradient=ft.LinearGradient(
                            colors=[Colors.NEON_CYAN, Colors.NEON_GREEN],
                            begin=ft.alignment.top_left,
                            end=ft.alignment.bottom_right,
                        ),
                    ),
                ] + ([
                    ft.Column(
                        controls=[
                            ft.Text(
                                user.full_name if user else "",
                                size=Typography.SIZE_SM,
                                weight=ft.FontWeight.W_500,
                                color=Colors.TEXT_PRIMARY,
                                no_wrap=True,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                user.role.upper() if user else "",
                                size=Typography.SIZE_XS,
                                color=Colors.NEON_CYAN,
                                letter_spacing=0.5,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                ] if expanded[0] else []),
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.all(10),
        )

    # Referência para o container principal para rebuild
    sidebar_col = ft.Column(controls=[], spacing=4, expand=True)
    sidebar_container = ft.Ref()

    def _rebuild(container=None):
        all_items = MENU_ITEMS[:]
        if state.is_superadmin:
            all_items += ADMIN_MENU_ITEMS

        width = Sizes.SIDEBAR_FULL if expanded[0] else Sizes.SIDEBAR_SLIM

        menu_controls = [build_menu_item(item) for item in all_items]

        sidebar_col.controls = [
            # Logo / Toggle
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            width=32,
                            height=32,
                            border_radius=8,
                            gradient=ft.LinearGradient(
                                colors=[Colors.NEON_CYAN, Colors.NEON_GREEN],
                                begin=ft.alignment.top_left,
                                end=ft.alignment.bottom_right,
                            ),
                            content=ft.Icon(ft.Icons.CHAT_BUBBLE, color=Colors.TEXT_ON_ACCENT, size=18),
                        ),
                    ] + ([
                        ft.Text("Atendimento", size=Typography.SIZE_MD, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                    ] if expanded[0] else []),
                    spacing=8,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN if expanded[0] else ft.MainAxisAlignment.CENTER,
                ),
                padding=ft.padding.all(12),
                on_click=toggle_expand,
                tooltip="Retrair/Expandir menu",
            ),

            ft.Container(height=8),
            ft.Divider(color=Colors.DARK_BG_ELEVATED, height=1),
            ft.Container(height=8),

            # Menu items
            *menu_controls,

            # Expansor
            ft.Container(expand=True),

            ft.Divider(color=Colors.DARK_BG_ELEVATED, height=1),
            ft.Container(height=8),

            # Tema toggle
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.DARK_MODE if state.is_dark_mode else ft.Icons.LIGHT_MODE,
                            icon_color=Colors.TEXT_SECONDARY,
                            icon_size=20,
                            on_click=lambda e: state.toggle_theme(),
                            tooltip="Alternar tema",
                        ),
                    ] + ([ft.Text("Tema", size=Typography.SIZE_SM, color=Colors.TEXT_SECONDARY)] if expanded[0] else []),
                    spacing=0,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ),

            # Logout
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.LOGOUT,
                            icon_color=Colors.ERROR,
                            icon_size=20,
                            on_click=lambda e: _do_logout(page),
                            tooltip="Sair",
                        ),
                    ] + ([ft.Text("Sair", size=Typography.SIZE_SM, color=Colors.ERROR)] if expanded[0] else []),
                    spacing=0,
                ),
            ),

            ft.Container(height=8),
            ft.Divider(color=Colors.DARK_BG_ELEVATED, height=1),
            _build_user_avatar(),
        ]

        if page:
            try:
                page.update()
            except Exception:
                pass

    _rebuild()

    def _do_logout(pg: ft.Page):
        try:
            from frontend.api_client import api
            api.logout()
        except Exception:
            pass
        state.logout()
        pg.go("/login")

    return ft.Container(
        content=ft.Column(
            controls=[sidebar_col],
            expand=True,
        ),
        width=Sizes.SIDEBAR_FULL if expanded[0] else Sizes.SIDEBAR_SLIM,
        bgcolor=Colors.DARK_BG_SURFACE,
        border=ft.border.only(right=ft.BorderSide(1, Colors.DARK_BG_ELEVATED)),
        animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT),
        padding=ft.padding.symmetric(horizontal=4, vertical=8),
    )
