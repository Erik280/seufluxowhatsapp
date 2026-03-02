"""
Frontend Flet - Entrypoint Principal
Sistema de Atendimento WhatsApp SaaS
"""
import flet as ft
import os
from frontend.theme import Colors, Typography, get_dark_theme, get_light_theme
from frontend.state import state
from frontend.api_client import api
from frontend.realtime import poller

# Importa páginas
from frontend.pages.login import LoginPage
from frontend.pages.dashboard import DashboardPage
from frontend.pages.broadcasts import BroadcastsPage
from frontend.pages.settings import SettingsPage
from frontend.pages.admin import AdminPage

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", "8080"))


def main(page: ft.Page):
    """Configuração principal da aplicação Flet."""

    # Configurações da janela
    page.title = "WhatsApp Atendimento | Transforma Futuro"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = get_dark_theme()
    page.dark_theme = get_dark_theme()
    page.bgcolor = Colors.DARK_BG_DEEP
    page.window_min_width = 900
    page.window_min_height = 600
    page.padding = 0
    page.spacing = 0
    page.fonts = {
        "Roboto": "https://fonts.gstatic.com/s/roboto/v32/KFOmCnqEu92Fr1Mu4mxK.woff2",
        "Roboto Mono": "https://fonts.gstatic.com/s/robotomono/v23/L0xuDF4xlVMF-BfR8bXMIhJHg45mwgGEFl0_3vq_ROW4.woff2",
    }

    # Listener para mudança de tema
    def _on_state_change(section: str, data=None):
        if section == "theme":
            page.theme_mode = ft.ThemeMode.DARK if state.is_dark_mode else ft.ThemeMode.LIGHT
            page.bgcolor = Colors.DARK_BG_DEEP if state.is_dark_mode else Colors.LIGHT_BG_MAIN
            try:
                page.update()
            except Exception:
                pass

    state.subscribe(_on_state_change)

    # Roteador de páginas
    def route_change(e: ft.RouteChangeEvent):
        page.controls.clear()
        page.overlay.clear()

        route = e.route

        # Protege rotas autenticadas
        if route != "/login" and not state.is_authenticated:
            # Tenta restaurar sessão
            page.go("/login")
            return

        if route == "/login" or route == "/":
            page.controls.append(LoginPage(page))

        elif route == "/dashboard" or route == "/chats":
            page.controls.append(DashboardPage(page))

        elif route == "/broadcasts":
            page.controls.append(BroadcastsPage(page))

        elif route == "/settings":
            page.controls.append(SettingsPage(page))

        elif route == "/admin":
            page.controls.append(AdminPage(page))

        else:
            # 404 - redireciona para login ou dashboard
            if state.is_authenticated:
                page.go("/dashboard")
            else:
                page.go("/login")
            return

        try:
            page.update()
        except Exception:
            pass

    def view_pop(e: ft.ViewPopEvent):
        page.views.pop()
        top_view = page.views[-1] if page.views else None
        if top_view:
            page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Inicia o poller de realtime (background)
    poller.start()

    # Configuração de api_client
    api.base_url = BACKEND_URL

    # Rota inicial
    page.go("/login")


if __name__ == "__main__":
    import flet as ft
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        port=FRONTEND_PORT,
        host="0.0.0.0",
    )
