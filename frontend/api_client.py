"""
Cliente HTTP para comunicação com o backend FastAPI
"""
import requests
from typing import Optional, Any
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


class APIClient:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.token: str = ""
        self.timeout = 30

    def set_token(self, token: str):
        self.token = token

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def _request(self, method: str, path: str, **kwargs) -> Optional[Any]:
        try:
            url = f"{self.base_url}{path}"
            response = requests.request(
                method,
                url,
                headers=self._headers(),
                timeout=self.timeout,
                **kwargs,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            try:
                detail = e.response.json().get("detail", str(e))
            except Exception:
                detail = str(e)
            raise APIError(detail, e.response.status_code if e.response else 500)
        except requests.exceptions.ConnectionError:
            raise APIError("Erro de conexão com o servidor. Verifique se o backend está rodando.", 503)
        except requests.exceptions.Timeout:
            raise APIError("Timeout na requisição", 408)
        except Exception as e:
            raise APIError(str(e), 500)

    # --- Auth ---
    def login(self, email: str, password: str) -> dict:
        return self._request("POST", "/auth/login", json={"email": email, "password": password})

    def logout(self) -> dict:
        return self._request("POST", "/auth/logout")

    def get_me(self) -> dict:
        return self._request("GET", "/auth/me")

    # --- Contacts ---
    def get_contacts(self, search: str = "", status: str = "", tag_id: str = "", limit: int = 50, offset: int = 0) -> list:
        params = {"search": search, "status": status, "tag_id": tag_id, "limit": limit, "offset": offset}
        return self._request("GET", "/contacts", params={k: v for k, v in params.items() if v})

    def get_contact(self, contact_id: str) -> dict:
        return self._request("GET", f"/contacts/{contact_id}")

    def update_contact(self, contact_id: str, data: dict) -> dict:
        return self._request("PUT", f"/contacts/{contact_id}", json=data)

    def set_contact_tags(self, contact_id: str, tag_ids: list) -> dict:
        return self._request("POST", f"/contacts/{contact_id}/tags", json={"tag_ids": tag_ids})

    def takeover(self, contact_id: str) -> dict:
        return self._request("POST", f"/contacts/{contact_id}/takeover")

    def release(self, contact_id: str) -> dict:
        return self._request("POST", f"/contacts/{contact_id}/release")

    def pause(self, contact_id: str) -> dict:
        return self._request("POST", f"/contacts/{contact_id}/pause")

    # --- Messages ---
    def get_messages(self, contact_id: str, limit: int = 50, offset: int = 0) -> list:
        return self._request("GET", f"/messages/{contact_id}", params={"limit": limit, "offset": offset})

    def send_message(self, contact_id: str, content: str, message_type: str = "text", media_url: str = None) -> dict:
        payload = {"contact_id": contact_id, "content": content, "message_type": message_type}
        if media_url:
            payload["media_url"] = media_url
        return self._request("POST", "/messages/send", json=payload)

    # --- Broadcasts ---
    def get_broadcasts(self, status: str = "", limit: int = 50) -> list:
        params = {"limit": limit}
        if status:
            params["status"] = status
        return self._request("GET", "/broadcasts", params=params)

    def create_broadcast(self, data: dict) -> dict:
        return self._request("POST", "/broadcasts", json=data)

    def cancel_broadcast(self, broadcast_id: str) -> dict:
        return self._request("DELETE", f"/broadcasts/{broadcast_id}")

    # --- Tags ---
    def get_tags(self) -> list:
        return self._request("GET", "/admin/tags")

    def create_tag(self, name: str, color: str) -> dict:
        return self._request("POST", "/admin/tags", json={"name": name, "color": color})

    def delete_tag(self, tag_id: str) -> dict:
        return self._request("DELETE", f"/admin/tags/{tag_id}")

    # --- Admin (SuperAdmin) ---
    def get_companies(self) -> list:
        return self._request("GET", "/admin/companies")

    def create_company(self, data: dict) -> dict:
        return self._request("POST", "/admin/companies", json=data)

    def get_all_users(self, company_id: str = "") -> list:
        params = {}
        if company_id:
            params["company_id"] = company_id
        return self._request("GET", "/admin/users", params=params)

    def create_user(self, data: dict) -> dict:
        return self._request("POST", "/admin/users", json=data)

    def get_logs(self, company_id: str = "", action: str = "") -> list:
        params = {}
        if company_id:
            params["company_id"] = company_id
        if action:
            params["action"] = action
        return self._request("GET", "/admin/logs", params=params)

    def get_stats(self) -> dict:
        return self._request("GET", "/admin/stats")


class APIError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code
        self.message = message


# Instância global
api = APIClient()
