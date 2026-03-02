"""
Webhook da Evolution API - core do sistema de atendimento
"""
import asyncio
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from backend.models.schemas import EvolutionWebhookPayload
from backend import database as db
from backend.redis_client import get_chat_status, set_chat_status
from backend.services import bot_service, evolution_service as evo, media_service
from backend.config import settings

router = APIRouter(prefix="/webhook", tags=["Webhook"])


@router.post("/evolution")
async def receive_evolution_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """
    Endpoint principal que recebe todos os eventos da Evolution API.
    Decide automaticamente entre Bot e Atendimento Humano via Redis.
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Payload inválido")

    event = payload.get("event", "")
    instance = payload.get("instance", "")

    # Apenas processar eventos de mensagens recebidas
    if event not in ("messages.upsert", "messages.update"):
        return {"status": "ignored", "event": event}

    data = payload.get("data", {})
    key = data.get("key", {})
    remote_jid = key.get("remoteJid", "")

    # Ignorar mensagens de grupo e mensagens enviadas pelo próprio número
    if evo.is_group_message(remote_jid):
        return {"status": "ignored", "reason": "group_message"}

    if key.get("fromMe", False):
        return {"status": "ignored", "reason": "own_message"}

    phone = evo.extract_phone_from_jid(remote_jid)
    if not phone:
        return {"status": "ignored", "reason": "no_phone"}

    # Extrai o conteúdo da mensagem
    msg_obj = data.get("message", {})
    message_text, message_type, media_url = _extract_message_content(msg_obj)

    # Busca a empresa pela instância
    company = await _get_company_by_instance(instance)
    if not company:
        return {"status": "error", "reason": "company_not_found", "instance": instance}

    company_id = company.get("id")

    # Processa em background para resposta rápida ao Evolution API
    background_tasks.add_task(
        _process_incoming_message,
        company=company,
        phone=phone,
        message_text=message_text,
        message_type=message_type,
        media_url=media_url,
        evolution_data=data,
    )

    return {"status": "queued"}


async def _process_incoming_message(
    company: dict,
    phone: str,
    message_text: str,
    message_type: str,
    media_url: str | None,
    evolution_data: dict,
):
    """Processamento assíncrono em background da mensagem recebida."""
    company_id = company.get("id")

    try:
        # Upsert contato (cria se não existe)
        contact = await db.upsert_contact(company_id, phone, {
            "last_interaction": "now()",
        })

        if not contact:
            print(f"[Webhook] Falha ao upsert contato {phone}")
            return

        contact_id = contact.get("id")

        # Se há mídia, faz upload para MinIO
        final_media_url = None
        if media_url and message_type != "text":
            apikey = company.get("evolution_apikey", "")
            final_media_url = await media_service.process_incoming_media(media_url, apikey=apikey)

        # Salva a mensagem no histórico
        await db.save_message(
            company_id=company_id,
            contact_id=contact_id,
            direction="in",
            message_type=message_type,
            content=message_text,
            media_url=final_media_url,
            evolution_message_id=evolution_data.get("key", {}).get("id"),
        )

        # Incrementa contador de não lidas
        sb = db.get_supabase()
        sb.rpc("increment_unread", {"contact_id": contact_id}).execute()

        # Verifica status BOT/HUMANO via Redis
        chat_status = await get_chat_status(phone, company_id)

        if chat_status == "human":
            # Atendimento humano ativo - apenas notifica via Realtime (já salvo acima)
            print(f"[Webhook] {phone} em modo HUMANO - mensagem encaminhada para agente")
            return

        elif chat_status == "paused":
            # Atendimento pausado - ignora completamente
            print(f"[Webhook] {phone} em modo PAUSADO - mensagem ignorada")
            return

        else:
            # Modo BOT - processa gatilhos de flow
            if message_text and message_type == "text":
                responded = await bot_service.process_message(contact, message_text, company)
                if responded:
                    print(f"[Webhook] Bot respondeu para {phone}")
                else:
                    print(f"[Webhook] Nenhum flow correspondeu para {phone}: '{message_text}'")

    except Exception as e:
        print(f"[Webhook] Erro no processamento: {e}")
        await db.create_log(company_id, "webhook_error", {"error": str(e), "phone": phone})


async def _get_company_by_instance(instance: str) -> dict | None:
    """Busca empresa pelo nome da instância Evolution."""
    try:
        sb = db.get_supabase()
        result = sb.table("companies") \
            .select("*") \
            .eq("evolution_instance", instance) \
            .eq("is_active", True) \
            .maybe_single() \
            .execute()
        return result.data
    except Exception as e:
        print(f"[Webhook] Erro ao buscar empresa por instância '{instance}': {e}")
        return None


def _extract_message_content(msg_obj: dict) -> tuple[str, str, str | None]:
    """
    Extrai o texto, tipo e URL de mídia de um objeto de mensagem Evolution.
    Retorna: (text, type, media_url)
    """
    # Texto simples
    if "conversation" in msg_obj:
        return msg_obj["conversation"], "text", None

    # Texto estendido (com formatação)
    if "extendedTextMessage" in msg_obj:
        return msg_obj["extendedTextMessage"].get("text", ""), "text", None

    # Imagem
    if "imageMessage" in msg_obj:
        img = msg_obj["imageMessage"]
        caption = img.get("caption", "")
        url = img.get("url", "") or img.get("directPath", "")
        return caption, "image", url

    # Vídeo
    if "videoMessage" in msg_obj:
        vid = msg_obj["videoMessage"]
        caption = vid.get("caption", "")
        url = vid.get("url", "") or vid.get("directPath", "")
        return caption, "video", url

    # Áudio / PTT
    if "audioMessage" in msg_obj:
        audio = msg_obj["audioMessage"]
        url = audio.get("url", "") or audio.get("directPath", "")
        return "[Mensagem de voz]", "audio", url

    # Documento
    if "documentMessage" in msg_obj:
        doc = msg_obj["documentMessage"]
        title = doc.get("title", "Documento")
        url = doc.get("url", "") or doc.get("directPath", "")
        return title, "document", url

    # Sticker
    if "stickerMessage" in msg_obj:
        return "[Sticker]", "sticker", None

    return "", "text", None
