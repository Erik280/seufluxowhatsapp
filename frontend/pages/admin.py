"""
Painel SuperAdmin - Visão global do sistema
"""
import flet as ft
import threading
from frontend.theme import Colors, Typography, Sizes, neon_button_style, ghost_button_style
from frontend.state import state
from frontend.api_client import api, APIError
from frontend.components.sidebar import build_sidebar


def AdminPage(page: ft.Page):
    """Painel de SuperAdmin com visão global."""

    if not state.is_superadmin:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.BLOCK, size=64, color=Colors.ERROR),
                    ft.Text("Acesso Restrito", size=Typography.SIZE_2XL, weight=ft.FontWeight.BOLD, color=Colors.ERROR),
                    ft.Text("Esta área é exclusiva para SuperAdmins.", size=Typography.SIZE_MD, color=Colors.TEXT_SECONDARY),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            expand=True,
            bgcolor=Colors.DARK_BG_MAIN,
            alignment=ft.alignment.center,
        )

    # Stats cards
    stat_companies = ft.Ref[ft.Text]()
    stat_users = ft.Ref[ft.Text]()
    stat_contacts = ft.Ref[ft.Text]()
    stat_messages = ft.Ref[ft.Text]()

    companies_list = ft.Column(spacing=8)
    logs_list = ft.Column(spacing=4)
    logs_loading = ft.ProgressRing(color=Colors.NEON_CYAN, width=24, height=24, stroke_width=2, visible=False)

    selected_tab = [0]

    # Formulário nova empresa
    new_company_name = ft.TextField(
        label="Nome da empresa",
        bgcolor=Colors.DARK_BG_ELEVATED, border_color=Colors.DARK_BG_ELEVATED,
        focused_border_color=Colors.NEON_CYAN,
        label_style=ft.TextStyle(color=Colors.TEXT_SECONDARY, size=Typography.SIZE_SM),
        text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY), cursor_color=Colors.NEON_CYAN,
        border_radius=Sizes.BORDER_RADIUS_SM,
    )
    new_company_cnpj = ft.TextField(
        label="CNPJ (opcional)",
        bgcolor=Colors.DARK_BG_ELEVATED, border_color=Colors.DARK_BG_ELEVATED,
        focused_border_color=Colors.NEON_CYAN,
        label_style=ft.TextStyle(color=Colors.TEXT_SECONDARY, size=Typography.SIZE_SM),
        text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY), cursor_color=Colors.NEON_CYAN,
        border_radius=Sizes.BORDER_RADIUS_SM,
    )
    company_form_status = ft.Text("", size=Typography.SIZE_SM, visible=False)

    def load_all():
        _load_stats()
        _load_companies()
        _load_logs()

    def _load_stats():
        try:
            stats = api.get_stats()
            if stat_companies.current:
                stat_companies.current.value = str(stats.get("total_companies", 0))
            if stat_users.current:
                stat_users.current.value = str(stats.get("total_users", 0))
            if stat_contacts.current:
                stat_contacts.current.value = str(stats.get("total_contacts", 0))
            if stat_messages.current:
                stat_messages.current.value = str(stats.get("total_messages", 0))
            try:
                page.update()
            except Exception:
                pass
        except Exception as e:
            print(f"[Admin] Erro stats: {e}")

    def _load_companies():
        try:
            companies = api.get_companies()
            companies_list.controls.clear()
            for c in companies:
                plan_color = {"active": Colors.SUCCESS, "suspended": Colors.ERROR, "trial": Colors.WARNING}.get(c.get("plan_status", "active"), Colors.TEXT_MUTED)
                companies_list.controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Text((c.get("name") or "?")[0].upper(), size=14, color=Colors.TEXT_ON_ACCENT, weight=ft.FontWeight.BOLD),
                                    width=40, height=40, border_radius=8,
                                    bgcolor=Colors.NEON_CYAN + "AA",
                                    alignment=ft.alignment.center,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(c.get("name", ""), size=Typography.SIZE_MD, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                                        ft.Text(f"CNPJ: {c.get('cnpj') or '-'}  |  Instância: {c.get('evolution_instance') or '-'}", size=Typography.SIZE_XS, color=Colors.TEXT_SECONDARY),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                                ft.Container(
                                    content=ft.Text(c.get("plan_status", "active").upper(), size=9, color=plan_color, weight=ft.FontWeight.BOLD),
                                    border=ft.border.all(1, plan_color + "60"),
                                    border_radius=4,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                ),
                            ],
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.all(14),
                        bgcolor=Colors.DARK_BG_SURFACE,
                        border_radius=Sizes.BORDER_RADIUS,
                        border=ft.border.all(1, Colors.DARK_BG_ELEVATED),
                    )
                )
            try:
                page.update()
            except Exception:
                pass
        except Exception as e:
            print(f"[Admin] Erro companies: {e}")

    def _load_logs():
        logs_loading.visible = True
        try:
            page.update()
        except Exception:
            pass
        try:
            logs = api.get_logs()
            logs_list.controls.clear()
            for log in logs[:50]:
                from datetime import datetime
                try:
                    dt = datetime.fromisoformat(log.get("created_at", "").replace("Z", "+00:00"))
                    time_str = dt.strftime("%d/%m %H:%M")
                except Exception:
                    time_str = ""
                action = log.get("action", "")
                company_name = (log.get("companies") or {}).get("name", "")
                user_name = (log.get("users") or {}).get("full_name", "Sys")
                logs_list.controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(time_str, size=9, color=Colors.TEXT_MUTED, width=65),
                                ft.Container(
                                    content=ft.Text(action, size=9, color=Colors.NEON_CYAN),
                                    bgcolor=Colors.NEON_CYAN + "15",
                                    border_radius=4,
                                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                ),
                                ft.Text(company_name, size=Typography.SIZE_XS, color=Colors.TEXT_SECONDARY, expand=True),
                                ft.Text(user_name, size=Typography.SIZE_XS, color=Colors.TEXT_MUTED),
                            ],
                            spacing=8,
                        ),
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        border_radius=Sizes.BORDER_RADIUS_SM,
                        bgcolor=Colors.DARK_BG_ELEVATED,
                    )
                )
            logs_loading.visible = False
            try:
                page.update()
            except Exception:
                pass
        except Exception as e:
            print(f"[Admin] Erro logs: {e}")
            logs_loading.visible = False

    def create_company():
        def _create():
            try:
                api.create_company({"name": new_company_name.value.strip(), "cnpj": new_company_cnpj.value.strip() or None})
                new_company_name.value = ""
                new_company_cnpj.value = ""
                company_form_status.value = "✓ Empresa criada!"
                company_form_status.color = Colors.SUCCESS
                company_form_status.visible = True
                _load_companies()
                try:
                    page.update()
                except Exception:
                    pass
            except APIError as e:
                company_form_status.value = f"✗ {e.message}"
                company_form_status.color = Colors.ERROR
                company_form_status.visible = True
                try:
                    page.update()
                except Exception:
                    pass

        threading.Thread(target=_create, daemon=True).start()

    # Inicia carregamento
    threading.Thread(target=load_all, daemon=True).start()

    def on_navigate(page_id: str):
        if page_id != "admin":
            page.go(f"/{page_id}")

    sidebar = build_sidebar(page, on_navigate)

    def _stat_card(label: str, ref, icon, color: str) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(icon, color=color, size=28),
                            ft.Container(expand=True),
                        ],
                    ),
                    ft.Text(ref=ref, value="...", size=Typography.SIZE_3XL, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                    ft.Text(label, size=Typography.SIZE_XS, color=Colors.TEXT_MUTED, letter_spacing=0.5),
                ],
                spacing=4,
            ),
            padding=ft.padding.all(20),
            bgcolor=Colors.DARK_BG_SURFACE,
            border_radius=Sizes.BORDER_RADIUS,
            border=ft.border.all(1, color + "20"),
            expand=True,
            shadow=ft.BoxShadow(blur_radius=20, color=color + "15", offset=ft.Offset(0, 4)),
        )

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
                                            ft.Text("🛡️ Super Admin", size=Typography.SIZE_2XL, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                                            ft.Text("Visão global do sistema SaaS", size=Typography.SIZE_SM, color=Colors.TEXT_SECONDARY),
                                        ],
                                        spacing=4,
                                        expand=True,
                                    ),
                                    ft.ElevatedButton(
                                        text="Atualizar",
                                        icon=ft.Icons.REFRESH,
                                        style=ghost_button_style(),
                                        on_click=lambda e: threading.Thread(target=load_all, daemon=True).start(),
                                    ),
                                ],
                            ),
                            padding=ft.padding.all(24),
                        ),

                        # Stats
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    _stat_card("EMPRESAS", stat_companies, ft.Icons.BUSINESS, Colors.NEON_CYAN),
                                    _stat_card("USUÁRIOS", stat_users, ft.Icons.GROUP, Colors.NEON_GREEN),
                                    _stat_card("CONTATOS", stat_contacts, ft.Icons.CONTACTS, Colors.WARNING),
                                    _stat_card("MENSAGENS", stat_messages, ft.Icons.MESSAGE, Colors.INFO),
                                ],
                                spacing=16,
                            ),
                            padding=ft.padding.symmetric(horizontal=24),
                        ),

                        ft.Container(height=16),

                        # Tabs: Empresas | Logs
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Tabs(
                                        selected_index=selected_tab[0],
                                        animation_duration=200,
                                        tabs=[
                                            ft.Tab(
                                                text="Empresas",
                                                icon=ft.Icons.BUSINESS,
                                                content=ft.Container(
                                                    content=ft.Row(
                                                        controls=[
                                                            # Lista de empresas
                                                            ft.Column(controls=[companies_list], expand=True, scroll=ft.ScrollMode.AUTO),
                                                            ft.Container(width=20),
                                                            # Formulário
                                                            ft.Container(
                                                                content=ft.Column(
                                                                    controls=[
                                                                        ft.Text("Adicionar Empresa", size=Typography.SIZE_MD, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                                                                        new_company_name,
                                                                        new_company_cnpj,
                                                                        company_form_status,
                                                                        ft.ElevatedButton(
                                                                            text="Criar Empresa",
                                                                            icon=ft.Icons.ADD_BUSINESS,
                                                                            style=neon_button_style(),
                                                                            on_click=lambda e: create_company(),
                                                                        ),
                                                                    ],
                                                                    spacing=12,
                                                                ),
                                                                width=320,
                                                                padding=ft.padding.all(20),
                                                                bgcolor=Colors.DARK_BG_SURFACE,
                                                                border_radius=Sizes.BORDER_RADIUS,
                                                                border=ft.border.all(1, Colors.NEON_CYAN + "20"),
                                                            ),
                                                        ],
                                                        expand=True,
                                                        vertical_alignment=ft.CrossAxisAlignment.START,
                                                    ),
                                                    padding=ft.padding.all(16),
                                                    expand=True,
                                                ),
                                            ),
                                            ft.Tab(
                                                text="Logs do Sistema",
                                                icon=ft.Icons.HISTORY,
                                                content=ft.Container(
                                                    content=ft.Column(
                                                        controls=[
                                                            logs_loading,
                                                            ft.Column(controls=[logs_list], scroll=ft.ScrollMode.AUTO, expand=True),
                                                        ],
                                                        expand=True,
                                                        spacing=8,
                                                    ),
                                                    padding=ft.padding.all(16),
                                                    expand=True,
                                                ),
                                            ),
                                        ],
                                        expand=True,
                                        label_color=Colors.NEON_CYAN,
                                        indicator_color=Colors.NEON_CYAN,
                                        unselected_label_color=Colors.TEXT_SECONDARY,
                                    ),
                                ],
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
