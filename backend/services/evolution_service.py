"""
Serviço de integração com a Evolution API
"""
import httpx
from backend.config import settings


async def _evolution_request(method: str, path: str, data: dict = None, apikey: str = None) -> dict:
    """Faz requisição autenticada para a Evolution API."""
    key = apikey or settings.EVOLUTION_API_KEY
    url = f"{settings.EVOLUTION_API_URL}{path}"
    headers = {"apikey": key, "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=30) as client:
        if method.upper() == "POST":
            response = await client.post(url, json=data, headers=headers)
        elif method.upper() == "GET":
            response = await client.get(url, headers=headers)
        else:
            response = await client.request(method.upper(), url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()


async def send_text_message(instance: str, phone: str, text: str, apikey: str = None) -> dict:
    """Envia mensagem de texto."""
    try:
        return await _evolution_request(
            "POST",
            f"/message/sendText/{instance}",
            data={"number": phone, "text": text},
            apikey=apikey,
        )
    except Exception as e:
        print(f"[Evolution] Erro ao enviar texto para {phone}: {e}")
        return {}


async def send_media_message(instance: str, phone: str, media_url: str, media_type: str, caption: str = "", apikey: str = None) -> dict:
    """Envia mensagem de mídia (image, video, document, audio)."""
    try:
        type_map = {
            "image": "image",
            "video": "video",
            "document": "document",
            "audio": "audio",
        }
        ev_type = type_map.get(media_type, "image")
        return await _evolution_request(
            "POST",
            f"/message/sendMedia/{instance}",
            data={
                "number": phone,
                "mediatype": ev_type,
                "media": media_url,
                "caption": caption,
            },
            apikey=apikey,
        )
    except Exception as e:
        print(f"[Evolution] Erro ao enviar mídia para {phone}: {e}")
        return {}


async def send_audio_message(instance: str, phone: str, audio_url: str, apikey: str = None) -> dict:
    """Envia áudio como PTT (Push To Talk)."""
    try:
        return await _evolution_request(
            "POST",
            f"/message/sendWhatsAppAudio/{instance}",
            data={"number": phone, "audio": audio_url},
            apikey=apikey,
        )
    except Exception as e:
        print(f"[Evolution] Erro ao enviar áudio para {phone}: {e}")
        return {}


async def send_typing(instance: str, phone: str, duration_ms: int = 3000, apikey: str = None):
    """Simula digitação no WhatsApp."""
    try:
        await _evolution_request(
            "POST",
            f"/chat/sendPresence/{instance}",
            data={"number": phone, "options": {"delay": duration_ms, "presence": "composing"}},
            apikey=apikey,
        )
    except Exception:
        pass  # Typing indicator é opcional, não deve quebrar o fluxo


async def get_instance_status(instance: str, apikey: str = None) -> dict:
    """Verifica o status da instância WhatsApp."""
    try:
        return await _evolution_request("GET", f"/instance/connectionState/{instance}", apikey=apikey)
    except Exception:
        return {"state": "unknown"}


def extract_phone_from_jid(remote_jid: str) -> str:
    """Extrai número de telefone do JID do WhatsApp (ex: 5511999@s.whatsapp.net → 5511999)"""
    return remote_jid.split("@")[0].split(":")[0]


def is_group_message(remote_jid: str) -> bool:
    """Verifica se é mensagem de grupo."""
    return "@g.us" in remote_jid
