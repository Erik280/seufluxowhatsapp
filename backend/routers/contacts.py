"""
CRM de Contatos - Dados, tags, takeover
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from backend.models.schemas import ContactUpdate, TagApply
from backend.routers.auth import get_current_user
from backend.redis_client import set_chat_status, delete_chat_status, get_chat_status
from backend import database as db
from datetime import datetime, timezone

router = APIRouter(prefix="/contacts", tags=["Contacts"])


@router.get("")
async def list_contacts(
    current_user: dict = Depends(get_current_user),
    search: str = Query(default="", description="Busca por nome ou telefone"),
    status: str = Query(default="", description="Filtro por chat_status"),
    tag_id: str = Query(default="", description="Filtro por tag"),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
):
    """Lista conversas/contatos da empresa com filtros."""
    company_id = current_user.get("company_id")
    is_superadmin = current_user.get("role") == "superadmin"

    sb = db.get_supabase()
    query = sb.table("contacts").select(
        "*, contact_tags(tag_id, tags(id, name, color))"
    )

    # SuperAdmin pode ver todos, caso contrário filtra por empresa
    if not is_superadmin:
        query = query.eq("company_id", company_id)

    if search:
        # Búsca parcial por nome ou telefone
        query = query.or_(f"full_name.ilike.%{search}%,phone.ilike.%{search}%")

    if status:
        query = query.eq("chat_status", status)

    result = query.order("last_interaction", desc=True).range(offset, offset + limit - 1).execute()
    return result.data or []


@router.get("/{contact_id}")
async def get_contact(
    contact_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Detalhes de um contato com tags e histórico resumido."""
    company_id = current_user.get("company_id")
    sb = db.get_supabase()

    result = sb.table("contacts").select(
        "*, contact_tags(tag_id, tags(id, name, color))"
    ).eq("id", contact_id).maybe_single().execute()

    contact = result.data
    if not contact:
        raise HTTPException(status_code=404, detail="Contato não encontrado")

    is_superadmin = current_user.get("role") == "superadmin"
    if not is_superadmin and contact.get("company_id") != company_id:
        raise HTTPException(status_code=403, detail="Sem acesso a este contato")

    # Enriquece com status do Redis
    redis_status = await get_chat_status(contact.get("phone", ""), contact.get("company_id", ""))
    contact["redis_chat_status"] = redis_status

    return contact


@router.put("/{contact_id}")
async def update_contact(
    contact_id: str,
    data: ContactUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Atualiza dados de CRM do contato."""
    company_id = current_user.get("company_id")
    sb = db.get_supabase()

    existing = sb.table("contacts").select("id, company_id, phone").eq("id", contact_id).maybe_single().execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Contato não encontrado")

    if current_user.get("role") != "superadmin" and existing.data.get("company_id") != company_id:
        raise HTTPException(status_code=403, detail="Sem acesso")

    update_data = data.model_dump(exclude_none=True)
    result = sb.table("contacts").update(update_data).eq("id", contact_id).execute()
    return result.data[0] if result.data else {}


@router.post("/{contact_id}/tags")
async def set_contact_tags(
    contact_id: str,
    body: TagApply,
    current_user: dict = Depends(get_current_user),
):
    """Define as tags de um contato (substitui as existentes)."""
    sb = db.get_supabase()

    # Remove tags antigas
    sb.table("contact_tags").delete().eq("contact_id", contact_id).execute()

    # Insere novas tags
    if body.tag_ids:
        rows = [{"contact_id": contact_id, "tag_id": tid} for tid in body.tag_ids]
        sb.table("contact_tags").insert(rows).execute()

    return {"status": "ok", "tag_ids": body.tag_ids}


@router.post("/{contact_id}/takeover")
async def takeover_conversation(
    contact_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Agente assume o atendimento - muda status para 'human'."""
    sb = db.get_supabase()
    result = sb.table("contacts").select("*").eq("id", contact_id).maybe_single().execute()
    contact = result.data
    if not contact:
        raise HTTPException(status_code=404, detail="Contato não encontrado")

    # Atualiza Redis
    await set_chat_status(contact["phone"], contact["company_id"], "human")

    # Atualiza banco
    sb.table("contacts").update({
        "chat_status": "human",
        "assigned_agent_id": current_user["id"],
        "unread_count": 0,
    }).eq("id", contact_id).execute()

    await db.create_log(
        contact["company_id"],
        "human_takeover",
        {"contact_id": contact_id, "agent": current_user["full_name"]},
        current_user["id"],
    )

    return {"status": "human", "agent": current_user["full_name"]}


@router.post("/{contact_id}/release")
async def release_conversation(
    contact_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Agente devolve o atendimento ao bot."""
    sb = db.get_supabase()
    result = sb.table("contacts").select("*").eq("id", contact_id).maybe_single().execute()
    contact = result.data
    if not contact:
        raise HTTPException(status_code=404, detail="Contato não encontrado")

    # Volta para bot
    await set_chat_status(contact["phone"], contact["company_id"], "bot")

    sb.table("contacts").update({
        "chat_status": "bot",
        "assigned_agent_id": None,
    }).eq("id", contact_id).execute()

    await db.create_log(
        contact["company_id"],
        "bot_release",
        {"contact_id": contact_id},
        current_user["id"],
    )

    return {"status": "bot"}


@router.post("/{contact_id}/pause")
async def pause_conversation(
    contact_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Pausa o atendimento (bot e humano ficam inativos)."""
    sb = db.get_supabase()
    result = sb.table("contacts").select("*").eq("id", contact_id).maybe_single().execute()
    contact = result.data
    if not contact:
        raise HTTPException(status_code=404, detail="Contato não encontrado")

    await set_chat_status(contact["phone"], contact["company_id"], "paused")
    sb.table("contacts").update({"chat_status": "paused"}).eq("id", contact_id).execute()

    return {"status": "paused"}
