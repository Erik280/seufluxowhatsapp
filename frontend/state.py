"""
Estado Global da Aplicação
"""
from dataclasses import dataclass, field
from typing import Optional, List, Callable, Any


@dataclass
class AppUser:
    id: str = ""
    full_name: str = ""
    email: str = ""
    role: str = "agent"
    company_id: str = ""
    company_name: str = ""
    avatar_url: str = ""


@dataclass
class AppState:
    # Autenticação
    token: str = ""
    user: Optional[AppUser] = None
    is_authenticated: bool = False

    # UI State
    is_dark_mode: bool = True
    sidebar_expanded: bool = True
    crm_panel_visible: bool = False
    current_page: str = "dashboard"

    # Chat
    selected_contact_id: str = ""
    selected_contact: Optional[dict] = None
    contacts: List[dict] = field(default_factory=list)
    messages: List[dict] = field(default_factory=list)
    tags: List[dict] = field(default_factory=list)

    # Listeners para atualização de UI
    _listeners: List[Callable] = field(default_factory=list, repr=False)

    def subscribe(self, callback: Callable):
        """Registra um callback para ser chamado quando o estado mudar."""
        self._listeners.append(callback)

    def notify_all(self, section: str = "all", data: Any = None):
        """Notifica todos os listeners de uma mudança de estado."""
        for listener in self._listeners:
            try:
                listener(section, data)
            except Exception as e:
                print(f"[State] Erro no listener: {e}")

    def set_user(self, user_data: dict, token: str):
        company_data = user_data.get("companies") or {}
        self.user = AppUser(
            id=user_data.get("id", ""),
            full_name=user_data.get("full_name", ""),
            email=user_data.get("email", ""),
            role=user_data.get("role", "agent"),
            company_id=user_data.get("company_id", ""),
            company_name=company_data.get("name", "") if isinstance(company_data, dict) else "",
            avatar_url=user_data.get("avatar_url", ""),
        )
        self.token = token
        self.is_authenticated = True
        self.notify_all("auth")

    def logout(self):
        self.token = ""
        self.user = None
        self.is_authenticated = False
        self.selected_contact_id = ""
        self.selected_contact = None
        self.contacts = []
        self.messages = []
        self.current_page = "login"
        self.notify_all("auth")

    def select_contact(self, contact: dict):
        self.selected_contact_id = contact.get("id", "")
        self.selected_contact = contact
        self.messages = []
        self.crm_panel_visible = False
        self.notify_all("contact_selected", contact)

    def update_contacts(self, contacts: list):
        self.contacts = contacts
        self.notify_all("contacts")

    def update_messages(self, messages: list):
        self.messages = messages
        self.notify_all("messages")

    def add_message(self, message: dict):
        self.messages.append(message)
        self.notify_all("new_message", message)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.notify_all("theme")

    def toggle_sidebar(self):
        self.sidebar_expanded = not self.sidebar_expanded
        self.notify_all("sidebar")

    def toggle_crm(self):
        self.crm_panel_visible = not self.crm_panel_visible
        self.notify_all("crm")

    def navigate(self, page: str):
        self.current_page = page
        self.notify_all("navigation", page)

    @property
    def is_superadmin(self) -> bool:
        return self.user and self.user.role == "superadmin"

    @property
    def is_admin(self) -> bool:
        return self.user and self.user.role in ("superadmin", "admin")


# Instância global singleton
state = AppState()
