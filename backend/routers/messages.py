"""
Mensagens - Histórico e Envio
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from backend.models.schemas import SendMessageRequest
from backend.routers.auth import get_current_user
from backend.services import evolution_service as evo
from backend import database as db

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.get("/{contact_id}")
async def get_message_history(
    contact_id: str,
    current_user: dict = Depends(get_current_user),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
):
    """Histórico de mensagens de um contato, paginado."""
    sb = db.get_supabase()

    result = sb.table("messages_history").select("*") \
        .eq("contact_id", contact_id) \
        .order("timestamp", desc=True) \
        .range(offset, offset + limit - 1) \
        .execute()

    # Retorna em ordem cronológica para a UI
    messages = result.data or []
    messages.reverse()
    return messages


@router.post("/send")
async def send_message(
    body: SendMessageRequest,
    current_user: dict = Depends(get_current_user),
):
    """Envia mensagem para um contato via Evolution API."""
    company_id = current_user.get("company_id")
    sb = db.get_supabase()

    # Busca contato e empresa
    contact_result = sb.table("contacts").select("*, companies(evolution_instance, evolution_apikey)").eq("id", body.contact_id).maybe_single().execute()
    contact = contact_result.data
    if not contact:
        raise HTTPException(status_code=404, detail="Contato não encontrado")

    is_superadmin = current_user.get("role") == "superadmin"
    if not is_superadmin and contact.get("company_id") != company_id:
        raise HTTPException(status_code=403, detail="Sem acesso a este contato")

    company_data = contact.get("companies", {}) or {}
    instance = company_data.get("evolution_instance", "")
    apikey = company_data.get("evolution_apikey", "")
    phone = contact.get("phone", "")

    if not instance or not phone:
        raise HTTPException(status_code=400, detail="Empresa sem instância Evolution configurada")

    # Envia via Evolution API
    if body.message_type.value == "text":
        await evo.send_text_message(instance, phone, body.content, apikey=apikey)
    elif body.message_type.value in ("image", "video", "document") and body.media_url:
        await evo.send_media_message(instance, phone, body.media_url, body.message_type.value, body.content, apikey=apikey)
    elif body.message_type.value == "audio" and body.media_url:
        await evo.send_audio_message(instance, phone, body.media_url, apikey=apikey)

    # Salva no histórico
    saved = await db.save_message(
        company_id=contact.get("company_id"),
        contact_id=body.contact_id,
        direction="out",
        message_type=body.message_type.value,
        content=body.content,
        media_url=body.media_url,
    )

    # Atualiza última interação
    sb.table("contacts").update({"last_interaction": "now()"}).eq("id", body.contact_id).execute()

    return saved
