"""
Sistema de Temas - Identidade Visual Transforma Futuro
Dark Mode como padrão com paleta neon ciano/verde
"""
import flet as ft


# ============================================================
# PALETA DE CORES
# ============================================================

class Colors:
    # Dark Mode
    DARK_BG_DEEP = "#050810"         # Fundo mais profundo
    DARK_BG_MAIN = "#0A0E1A"         # Fundo principal
    DARK_BG_SURFACE = "#111827"      # Cards e superfícies
    DARK_BG_ELEVATED = "#1A2235"     # Elementos elevados
    DARK_BG_HOVER = "#1E2840"        # Hover state

    # Neon Accent
    NEON_CYAN = "#00E5CC"            # Ciano primário
    NEON_CYAN_DARK = "#00B8A0"       # Ciano escuro
    NEON_GREEN = "#00FF88"           # Verde neon
    NEON_GREEN_DARK = "#00CC66"      # Verde escuro

    # Gradients (expressos como cores de início e fim)
    GRADIENT_START = "#00E5CC"
    GRADIENT_END = "#00FF88"

    # Text
    TEXT_PRIMARY = "#F0F4FF"         # Texto principal
    TEXT_SECONDARY = "#8899BB"       # Texto secundário
    TEXT_MUTED = "#445577"           # Texto silenciado
    TEXT_ON_ACCENT = "#050810"       # Texto sobre botões neon

    # Status
    STATUS_BOT = "#00E5CC"           # Bot ativo
    STATUS_HUMAN = "#00FF88"         # Humano ativo
    STATUS_PAUSED = "#FFA500"        # Pausado
    STATUS_ONLINE = "#00FF88"        # Online
    STATUS_OFFLINE = "#445577"       # Offline

    # Alerts & States
    SUCCESS = "#00FF88"
    WARNING = "#FFA500"
    ERROR = "#FF4466"
    INFO = "#00E5CC"

    # Message Bubbles
    BUBBLE_IN = "#1A2235"            # Mensagem recebida
    BUBBLE_OUT = "#00B8A0"           # Mensagem enviada
    BUBBLE_OUT_TEXT = "#050810"      # Texto de msg enviada

    # Light Mode
    LIGHT_BG_MAIN = "#F0F4FF"
    LIGHT_BG_SURFACE = "#FFFFFF"
    LIGHT_BG_ELEVATED = "#E8EDF8"
    LIGHT_TEXT_PRIMARY = "#0A0E1A"
    LIGHT_TEXT_SECONDARY = "#445577"


# ============================================================
# TIPOGRAFIA
# ============================================================

class Typography:
    FONT_PRIMARY = "Roboto"
    FONT_MONO = "Roboto Mono"

    SIZE_XS = 10
    SIZE_SM = 12
    SIZE_MD = 14
    SIZE_LG = 16
    SIZE_XL = 20
    SIZE_2XL = 24
    SIZE_3XL = 32
    SIZE_4XL = 40


# ============================================================
# ESPAÇAMENTO & DIMENSÕES
# ============================================================

class Sizes:
    SIDEBAR_SLIM = 64        # Sidebar retrátil (apenas ícones)
    SIDEBAR_FULL = 220       # Sidebar expandida
    CHAT_LIST_WIDTH = 320    # Painel de lista de conversas
    CRM_PANEL_WIDTH = 300    # Painel direito CRM

    BORDER_RADIUS = 12
    BORDER_RADIUS_SM = 8
    BORDER_RADIUS_LG = 20

    PADDING_SM = 8
    PADDING_MD = 16
    PADDING_LG = 24

    INPUT_HEIGHT = 44
    BUTTON_HEIGHT = 40
    AVATAR_SM = 36
    AVATAR_MD = 48
    AVATAR_LG = 64


# ============================================================
# TEMA DARK (padrão)
# ============================================================

def get_dark_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            brightness=ft.Brightness.DARK,
            primary=Colors.NEON_CYAN,
            on_primary=Colors.TEXT_ON_ACCENT,
            secondary=Colors.NEON_GREEN,
            surface=Colors.DARK_BG_SURFACE,
            background=Colors.DARK_BG_MAIN,
            on_background=Colors.TEXT_PRIMARY,
            on_surface=Colors.TEXT_PRIMARY,
            error=Colors.ERROR,
        ),
        font_family=Typography.FONT_PRIMARY,
        scaffold_content_color=Colors.TEXT_PRIMARY,
    )


def get_light_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            brightness=ft.Brightness.LIGHT,
            primary=Colors.NEON_CYAN_DARK,
            on_primary=Colors.LIGHT_TEXT_PRIMARY,
            secondary=Colors.NEON_GREEN_DARK,
            surface=Colors.LIGHT_BG_SURFACE,
            background=Colors.LIGHT_BG_MAIN,
            on_background=Colors.LIGHT_TEXT_PRIMARY,
            on_surface=Colors.LIGHT_TEXT_PRIMARY,
        ),
        font_family=Typography.FONT_PRIMARY,
    )


# ============================================================
# UTILITÁRIOS DE ESTILO
# ============================================================

def glow_style(color: str = Colors.NEON_CYAN, blur: int = 15, spread: int = 2) -> ft.BoxShadow:
    """Efeito de brilho neon."""
    return ft.BoxShadow(
        blur_radius=blur,
        spread_radius=spread,
        color=color + "66",  # 40% de opacidade
    )


def card_style(bg: str = Colors.DARK_BG_SURFACE, border: bool = True) -> dict:
    """Estilo padrão de card."""
    return dict(
        bgcolor=bg,
        border_radius=Sizes.BORDER_RADIUS,
        border=ft.border.all(1, Colors.NEON_CYAN + "20") if border else None,
        shadow=ft.BoxShadow(
            blur_radius=20,
            spread_radius=0,
            color="#000000AA",
            offset=ft.Offset(0, 4),
        ),
    )


def neon_button_style() -> ft.ButtonStyle:
    """Estilo de botão neon primário."""
    return ft.ButtonStyle(
        bgcolor={
            ft.ControlState.DEFAULT: Colors.NEON_CYAN,
            ft.ControlState.HOVERED: Colors.NEON_GREEN,
            ft.ControlState.PRESSED: Colors.NEON_CYAN_DARK,
        },
        color={
            ft.ControlState.DEFAULT: Colors.TEXT_ON_ACCENT,
        },
        shape=ft.RoundedRectangleBorder(radius=Sizes.BORDER_RADIUS_SM),
        shadow_color=Colors.NEON_CYAN + "66",
        elevation={"default": 4, "hovered": 8},
    )


def ghost_button_style() -> ft.ButtonStyle:
    """Botão transparente com borda neon."""
    return ft.ButtonStyle(
        bgcolor={
            ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
            ft.ControlState.HOVERED: Colors.NEON_CYAN + "15",
        },
        color={
            ft.ControlState.DEFAULT: Colors.NEON_CYAN,
        },
        side={
            ft.ControlState.DEFAULT: ft.BorderSide(1, Colors.NEON_CYAN + "60"),
            ft.ControlState.HOVERED: ft.BorderSide(1, Colors.NEON_CYAN),
        },
        shape=ft.RoundedRectangleBorder(radius=Sizes.BORDER_RADIUS_SM),
    )
