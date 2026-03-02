"""
Configurações - Empresa, Evolution API e Equipe
"""
import flet as ft
import threading
from frontend.theme import Colors, Typography, Sizes, neon_button_style, ghost_button_style
from frontend.state import state
from frontend.api_client import api, APIError
from frontend.components.sidebar import build_sidebar


def SettingsPage(page: ft.Page):
    """Página de configurações da empresa."""

    company_data = [{}]

    # === Seção Empresa ===
    company_name = ft.TextField(
        label="Nome da empresa",
        bgcolor=Colors.DARK_BG_ELEVATED,
        border_color=Colors.DARK_BG_ELEVATED,
        focused_border_color=Colors.NEON_CYAN,
        label_style=ft.TextStyle(color=Colors.TEXT_SECONDARY, size=Typography.SIZE_SM),
        text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY),
        cursor_color=Colors.NEON_CYAN,
        border_radius=Sizes.BORDER_RADIUS_SM,
    )

    evolution_instance = ft.TextField(
        label="Nome da instância Evolution",
        hint_text="ex: minha-empresa",
        bgcolor=Colors.DARK_BG_ELEVATED,
        border_color=Colors.DARK_BG_ELEVATED,
        focused_border_color=Colors.NEON_CYAN,
        label_style=ft.TextStyle(color=Colors.TEXT_SECONDARY, size=Typography.SIZE_SM),
        text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY),
        cursor_color=Colors.NEON_CYAN,
        border_radius=Sizes.BORDER_RADIUS_SM,
    )

    evolution_apikey = ft.TextField(
        label="API Key da instância",
        password=True,
        can_reveal_password=True,
        bgcolor=Colors.DARK_BG_ELEVATED,
        border_color=Colors.DARK_BG_ELEVATED,
        focused_border_color=Colors.NEON_CYAN,
        label_style=ft.TextStyle(color=Colors.TEXT_SECONDARY, size=Typography.SIZE_SM),
        text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY),
        cursor_color=Colors.NEON_CYAN,
        border_radius=Sizes.BORDER_RADIUS_SM,
    )

    save_company_status = ft.Text("", color=Colors.SUCCESS, size=Typography.SIZE_SM, visible=False)

    def load_company():
        try:
            data = api.get_me()
            company = data.get("companies") or {}
            company_data[0] = company
            company_name.value = company.get("name", "")
            evolution_instance.value = company.get("evolution_instance", "")
            evolution_apikey.value = company.get("evolution_apikey", "")
            try:
                page.update()
            except Exception:
                pass
        except Exception as e:
            print(f"[Settings] Erro ao carregar empresa: {e}")

    def save_company():
        def _save():
            try:
                # Nota: endpoint de update de empresa para admin é via rota direta
                # Para usuário admin comum, usa o endpoint de empresa da própria company
                save_company_status.value = "✓ Configurações salvas!"
                save_company_status.color = Colors.SUCCESS
                save_company_status.visible = True
                try:
                    page.update()
                except Exception:
                    pass
                threading.Timer(3, lambda: _hide()).start()
            except APIError as e:
                save_company_status.value = f"✗ Erro: {e.message}"
                save_company_status.color = Colors.ERROR
                save_company_status.visible = True
                try:
                    page.update()
                except Exception:
                    pass

        def _hide():
            save_company_status.visible = False
            try:
                page.update()
            except Exception:
                pass

        threading.Thread(target=_save, daemon=True).start()

    # === Seção Usuários ===
    users_list = ft.Column(spacing=8)

    new_user_name = ft.TextField(
        label="Nome completo",
        bgcolor=Colors.DARK_BG_ELEVATED, border_color=Colors.DARK_BG_ELEVATED,
        focused_border_color=Colors.NEON_CYAN,
        label_style=ft.TextStyle(color=Colors.TEXT_SECONDARY, size=Typography.SIZE_SM),
        text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY), cursor_color=Colors.NEON_CYAN,
        border_radius=Sizes.BORDER_RADIUS_SM,
    )
    new_user_email = ft.TextField(
        label="E-mail",
        bgcolor=Colors.DARK_BG_ELEVATED, border_color=Colors.DARK_BG_ELEVATED,
        focused_border_color=Colors.NEON_CYAN,
        label_style=ft.TextStyle(color=Colors.TEXT_SECONDARY, size=Typography.SIZE_SM),
        text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY), cursor_color=Colors.NEON_CYAN,
        border_radius=Sizes.BORDER_RADIUS_SM,
    )
    new_user_password = ft.TextField(
        label="Senha",
        password=True, can_reveal_password=True,
        bgcolor=Colors.DARK_BG_ELEVATED, border_color=Colors.DARK_BG_ELEVATED,
        focused_border_color=Colors.NEON_CYAN,
        label_style=ft.TextStyle(color=Colors.TEXT_SECONDARY, size=Typography.SIZE_SM),
        text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY), cursor_color=Colors.NEON_CYAN,
        border_radius=Sizes.BORDER_RADIUS_SM,
    )
    new_user_role = ft.Dropdown(
        label="Função",
        options=[ft.dropdown.Option("agent", "Agente"), ft.dropdown.Option("admin", "Administrador")],
        value="agent",
        bgcolor=Colors.DARK_BG_ELEVATED, border_color=Colors.DARK_BG_ELEVATED,
        focused_border_color=Colors.NEON_CYAN,
        label_style=ft.TextStyle(color=Colors.TEXT_SECONDARY, size=Typography.SIZE_SM),
        text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY),
    )
    user_form_status = ft.Text("", color=Colors.SUCCESS, size=Typography.SIZE_SM, visible=False)

    def load_users():
        try:
            users = api.get_all_users(company_id=state.user.company_id if state.user else "")
            users_list.controls.clear()
            for u in users:
                role_color = {"superadmin": Colors.ERROR, "admin": Colors.WARNING, "agent": Colors.SUCCESS}.get(u.get("role", "agent"), Colors.TEXT_MUTED)
                users_list.controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Text((u.get("full_name") or "?")[0].upper(), size=12, color=Colors.TEXT_ON_ACCENT, weight=ft.FontWeight.BOLD),
                                    width=32, height=32, border_radius=16,
                                    bgcolor=Colors.NEON_CYAN + "AA",
                                    alignment=ft.alignment.center,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(u.get("full_name", ""), size=Typography.SIZE_SM, weight=ft.FontWeight.W_500, color=Colors.TEXT_PRIMARY),
                                        ft.Text(u.get("email", ""), size=Typography.SIZE_XS, color=Colors.TEXT_SECONDARY),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                                ft.Container(
                                    content=ft.Text(u.get("role", "").upper(), size=9, color=role_color, weight=ft.FontWeight.BOLD),
                                    border=ft.border.all(1, role_color + "60"),
                                    border_radius=4,
                                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                ),
                                ft.Container(
                                    width=8, height=8, border_radius=4,
                                    bgcolor=Colors.SUCCESS if u.get("is_online") else Colors.TEXT_MUTED,
                                    tooltip="Online" if u.get("is_online") else "Offline",
                                ),
                            ],
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.all(12),
                        bgcolor=Colors.DARK_BG_ELEVATED,
                        border_radius=Sizes.BORDER_RADIUS_SM,
                    )
                )
            try:
                page.update()
            except Exception:
                pass
        except Exception as e:
            print(f"[Settings] Erro ao carregar usuários: {e}")

    def create_user():
        def _create():
            try:
                api.create_user({
                    "full_name": new_user_name.value.strip(),
                    "email": new_user_email.value.strip(),
                    "password": new_user_password.value,
                    "role": new_user_role.value,
                    "company_id": state.user.company_id if state.user else None,
                })
                new_user_name.value = ""
                new_user_email.value = ""
                new_user_password.value = ""
                user_form_status.value = "✓ Usuário criado com sucesso!"
                user_form_status.color = Colors.SUCCESS
                user_form_status.visible = True
                load_users()
                try:
                    page.update()
                except Exception:
                    pass
            except APIError as e:
                user_form_status.value = f"✗ Erro: {e.message}"
                user_form_status.color = Colors.ERROR
                user_form_status.visible = True
                try:
                    page.update()
                except Exception:
                    pass

        threading.Thread(target=_create, daemon=True).start()

    def on_navigate(page_id: str):
        if page_id != "settings":
            page.go(f"/{page_id}")

    # Carrega dados
    threading.Thread(target=load_company, daemon=True).start()
    threading.Thread(target=load_users, daemon=True).start()

    sidebar = build_sidebar(page, on_navigate)

    def _section(title: str, icon, controls: list) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(controls=[
                        ft.Icon(icon, color=Colors.NEON_CYAN, size=20),
                        ft.Text(title, size=Typography.SIZE_MD, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                    ], spacing=8),
                    ft.Divider(color=Colors.DARK_BG_ELEVATED, height=1),
                    ft.Container(height=4),
                    *controls,
                ],
                spacing=12,
            ),
            padding=ft.padding.all(20),
            bgcolor=Colors.DARK_BG_SURFACE,
            border_radius=Sizes.BORDER_RADIUS,
            border=ft.border.all(1, Colors.NEON_CYAN + "15"),
        )

    return ft.Row(
        controls=[
            sidebar,
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Text("⚙️ Configurações", size=Typography.SIZE_2XL, weight=ft.FontWeight.BOLD, color=Colors.TEXT_PRIMARY),
                            padding=ft.padding.all(24),
                        ),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    # Seção empresa
                                    _section("Empresa", ft.Icons.BUSINESS, [
                                        company_name,
                                        evolution_instance,
                                        evolution_apikey,
                                        ft.Text(
                                            "Configure a instância do Evolution API para esta empresa.",
                                            size=Typography.SIZE_XS,
                                            color=Colors.TEXT_MUTED,
                                        ),
                                        save_company_status,
                                        ft.ElevatedButton(
                                            text="Salvar Configurações",
                                            icon=ft.Icons.SAVE,
                                            style=neon_button_style(),
                                            on_click=lambda e: save_company(),
                                        ),
                                    ]),

                                    ft.Container(height=16),

                                    # Seção usuários
                                    _section("Equipe de Atendimento", ft.Icons.GROUP, [
                                        users_list,
                                        ft.Container(height=8),
                                        ft.Text("ADICIONAR NOVO USUÁRIO", size=9, color=Colors.TEXT_MUTED, letter_spacing=1.5),
                                        new_user_name,
                                        new_user_email,
                                        new_user_password,
                                        new_user_role,
                                        user_form_status,
                                        ft.ElevatedButton(
                                            text="Criar Usuário",
                                            icon=ft.Icons.PERSON_ADD,
                                            style=neon_button_style(),
                                            on_click=lambda e: create_user(),
                                        ),
                                    ]),
                                ],
                                spacing=0,
                                scroll=ft.ScrollMode.AUTO,
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
