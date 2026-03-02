"""
Listener de Realtime do Supabase
Monitora novas mensagens e atualiza o estado da aplicação
"""
import threading
import time
import requests
from frontend.state import state
from frontend.api_client import api


class RealtimePoller:
    """
    Polling de novas mensagens como alternativa ao Supabase Realtime WebSocket.
    Faz polling a cada 3 segundos quando há um contato selecionado.
    """

    def __init__(self, interval: float = 3.0):
        self.interval = interval
        self._running = False
        self._thread: threading.Thread | None = None
        self._last_message_id: str = ""
        self._last_contact_id: str = ""
        self._last_contact_count: int = 0

    def start(self):
        """Inicia o polling em background."""
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
        print("[Realtime] Poller iniciado")

    def stop(self):
        """Para o polling."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        print("[Realtime] Poller parado")

    def _poll_loop(self):
        """Loop principal de polling."""
        while self._running:
            try:
                if state.is_authenticated:
                    # Atualiza lista de contatos periodicamente
                    self._poll_contacts()

                    # Atualiza mensagens do contato selecionado
                    if state.selected_contact_id:
                        self._poll_messages()

            except Exception as e:
                print(f"[Realtime] Erro no polling: {e}")

            time.sleep(self.interval)

    def _poll_contacts(self):
        """Busca atualização na lista de contatos."""
        try:
            contacts = api.get_contacts(limit=50)
            if contacts != state.contacts:
                state.update_contacts(contacts)
        except Exception:
            pass

    def _poll_messages(self):
        """Busca novas mensagens do contato selecionado."""
        try:
            contact_id = state.selected_contact_id
            if not contact_id:
                return

            # Detectou mudança de contato
            if contact_id != self._last_contact_id:
                self._last_contact_id = contact_id
                self._last_message_id = ""

            messages = api.get_messages(contact_id, limit=50)
            if not messages:
                return

            # Verifica se há mensagens novas
            latest_id = messages[-1].get("id", "")
            if latest_id != self._last_message_id:
                self._last_message_id = latest_id
                # Só atualiza se realmente mudou
                current_ids = {m.get("id") for m in state.messages}
                new_ids = {m.get("id") for m in messages}
                if current_ids != new_ids:
                    state.update_messages(messages)

        except Exception:
            pass


# Instância global
poller = RealtimePoller(interval=3.0)
