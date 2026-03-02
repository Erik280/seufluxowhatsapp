"""
Página de Login - Design Futurista Transforma Futuro
"""
import flet as ft
from frontend.theme import Colors, Typography, Sizes, neon_button_style, ghost_button_style
from frontend.api_client import api, APIError
from frontend.state import state


def LoginPage(page: ft.Page):
    """Constrói e retorna a página de login."""

    # --- State ---
    loading = ft.Ref[bool]()
    loading.current = False

    # --- Controls ---
    email_field = ft.TextField(
        label="E-mail",
        hint_text="seu@email.com",
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        keyboard_type=ft.KeyboardType.EMAIL,
        bgcolor=Colors.DARK_BG_ELEVATED,
        border_color=Colors.NEON_CYAN + "40",
        focused_border_color=Colors.NEON_CYAN,
        label_style=ft.TextStyle(color=Colors.TEXT_SECONDARY),
        text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY),
        cursor_color=Colors.NEON_CYAN,
        height=Sizes.INPUT_HEIGHT + 12,
        border_radius=Sizes.BORDER_RADIUS_SM,
        autofocus=True,
    )

    password_field = ft.TextField(
        label="Senha",
        hint_text="••••••••",
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        password=True,
        can_reveal_password=True,
        bgcolor=Colors.DARK_BG_ELEVATED,
        border_color=Colors.NEON_CYAN + "40",
        focused_border_color=Colors.NEON_CYAN,
        label_style=ft.TextStyle(color=Colors.TEXT_SECONDARY),
        text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY),
        cursor_color=Colors.NEON_CYAN,
        height=Sizes.INPUT_HEIGHT + 12,
        border_radius=Sizes.BORDER_RADIUS_SM,
    )

    error_text = ft.Text(
        value="",
        color=Colors.ERROR,
        size=Typography.SIZE_SM,
        visible=False,
        text_align=ft.TextAlign.CENTER,
    )

    login_btn = ft.ElevatedButton(
        text="ENTRAR",
        icon=ft.Icons.LOGIN,
        width=320,
        height=Sizes.BUTTON_HEIGHT + 8,
        style=neon_button_style(),
        on_click=lambda e: do_login(e),
    )

    loading_indicator = ft.ProgressRing(
        color=Colors.NEON_CYAN,
        bgcolor=Colors.DARK_BG_ELEVATED,
        width=24,
        height=24,
        stroke_width=2,
        visible=False,
    )

    def show_error(msg: str):
        error_text.value = msg
        error_text.visible = True
        page.update()

    def clear_error():
        error_text.visible = False
        page.update()

    def do_login(e):
        email = email_field.value.strip()
        password = password_field.value.strip()

        if not email or not password:
            show_error("Preencha e-mail e senha")
            return

        clear_error()
        login_btn.visible = False
        loading_indicator.visible = True
        page.update()

        try:
            result = api.login(email, password)
            api.set_token(result["access_token"])
            state.set_user(result["user"], result["access_token"])
            page.go("/dashboard")
        except APIError as ex:
            show_error(ex.message)
        except Exception as ex:
            show_error(f"Erro inesperado: {ex}")
        finally:
            login_btn.visible = True
            loading_indicator.visible = False
            page.update()

    # Enter key no campo de senha
    password_field.on_submit = do_login
    email_field.on_submit = lambda e: password_field.focus()

    # --- Layout ---
    # Partículas de fundo (efeito visual)
    bg_particles = ft.Stack([
        # Círculo de brilho grande
        ft.Container(
            width=600,
            height=600,
            border_radius=300,
            bgcolor=Colors.NEON_CYAN + "08",
            shadow=ft.BoxShadow(blur_radius=150, color=Colors.NEON_CYAN + "20"),
            left=-150,
            top=-100,
        ),
        ft.Container(
            width=400,
            height=400,
            border_radius=200,
            bgcolor=Colors.NEON_GREEN + "06",
            shadow=ft.BoxShadow(blur_radius=100, color=Colors.NEON_GREEN + "15"),
            right=-100,
            bottom=-80,
        ),
    ])

    # Logo / Brand
    brand = ft.Column(
        controls=[
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            width=48,
                            height=48,
                            border_radius=12,
                            gradient=ft.LinearGradient(
                                begin=ft.alignment.top_left,
                                end=ft.alignment.bottom_right,
                                colors=[Colors.NEON_CYAN, Colors.NEON_GREEN],
                            ),
                            content=ft.Icon(ft.Icons.CHAT_BUBBLE, color=Colors.TEXT_ON_ACCENT, size=28),
                            shadow=ft.BoxShadow(blur_radius=20, color=Colors.NEON_CYAN + "50"),
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    "Transforma",
                                    size=Typography.SIZE_XL,
                                    weight=ft.FontWeight.BOLD,
                                    color=Colors.TEXT_PRIMARY,
                                ),
                                ft.Text(
                                    "FUTURO",
                                    size=Typography.SIZE_XL,
                                    weight=ft.FontWeight.BOLD,
                                    color=Colors.NEON_CYAN,
                                    letter_spacing=3,
                                ),
                            ],
                            spacing=0,
                        ),
                    ],
                    spacing=12,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
            ),
            ft.Text(
                "Sistema de Atendimento WhatsApp",
                size=Typography.SIZE_SM,
                color=Colors.TEXT_SECONDARY,
                text_align=ft.TextAlign.CENTER,
                letter_spacing=1,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=8,
    )

    # Card de Login
    login_card = ft.Container(
        content=ft.Column(
            controls=[
                brand,
                ft.Container(height=32),
                ft.Text(
                    "Faça seu login",
                    size=Typography.SIZE_LG,
                    weight=ft.FontWeight.W_500,
                    color=Colors.TEXT_PRIMARY,
                ),
                ft.Container(height=4),
                email_field,
                ft.Container(height=8),
                password_field,
                ft.Container(height=4),
                error_text,
                ft.Container(height=16),
                ft.Column(
                    controls=[login_btn, loading_indicator],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                ft.Container(height=16),
                ft.Row(
                    controls=[
                        ft.Container(expand=True, height=1, bgcolor=Colors.DARK_BG_ELEVATED),
                        ft.Text("•", color=Colors.TEXT_MUTED, size=10),
                        ft.Container(expand=True, height=1, bgcolor=Colors.DARK_BG_ELEVATED),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(height=16),
                ft.Text(
                    "WhatsApp Atendimento SaaS v1.0",
                    size=Typography.SIZE_XS,
                    color=Colors.TEXT_MUTED,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        width=400,
        padding=ft.padding.all(40),
        border_radius=20,
        bgcolor=Colors.DARK_BG_SURFACE,
        border=ft.border.all(1, Colors.NEON_CYAN + "25"),
        shadow=ft.BoxShadow(
            blur_radius=60,
            color="#000000CC",
            offset=ft.Offset(0, 20),
        ),
    )

    return ft.Stack(
        controls=[
            # Fundo
            ft.Container(
                width=page.width or 1200,
                height=page.height or 800,
                bgcolor=Colors.DARK_BG_DEEP,
            ),
            bg_particles,
            # Grid de linhas sutis
            ft.Container(
                width=page.width or 1200,
                height=page.height or 800,
                opacity=0.03,
                content=ft.Image(
                    src="https://www.transparenttextures.com/patterns/carbon-fibre.png",
                    fit=ft.ImageFit.COVER,
                ),
            ),
            # Card centralizado
            ft.Container(
                content=login_card,
                alignment=ft.alignment.center,
                expand=True,
            ),
        ],
        expand=True,
    )
