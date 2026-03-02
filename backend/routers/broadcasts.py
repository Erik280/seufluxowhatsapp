"""
Broadcasts - Criação, Agendamento e Gerenciamento
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from backend.models.schemas import BroadcastCreate
from backend.routers.auth import get_current_user, get_admin_or_above
from backend import database as db
from datetime import datetime, timezone

router = APIRouter(prefix="/broadcasts", tags=["Broadcasts"])


@router.get("")
async def list_broadcasts(
    current_user: dict = Depends(get_current_user),
    status: str = Query(default="", description="Filtro por status"),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
):
    """Lista broadcasts da empresa."""
    company_id = current_user.get("company_id")
    is_superadmin = current_user.get("role") == "superadmin"
    sb = db.get_supabase()

    query = sb.table("broadcasts").select("*, users(full_name)")
    if not is_superadmin:
        query = query.eq("company_id", company_id)
    if status:
        query = query.eq("status", status)

    result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
    return result.data or []


@router.post("")
async def create_broadcast(
    body: BroadcastCreate,
    current_user: dict = Depends(get_admin_or_above),
):
    """Cria um broadcast agendado."""
    company_id = current_user.get("company_id")
    sb = db.get_supabase()

    scheduled_at = body.scheduled_at.isoformat() if body.scheduled_at else datetime.now(timezone.utc).isoformat()

    result = sb.table("broadcasts").insert({
        "company_id": company_id,
        "title": body.title,
        "content": body.content,
        "media_url": body.media_url,
        "media_type": body.media_type,
        "target_tags": body.target_tags or [],
        "target_phone_list": body.target_phone_list or [],
        "scheduled_at": scheduled_at,
        "status": "pending",
        "created_by": current_user["id"],
    }).execute()

    broadcast = result.data[0] if result.data else {}
    await db.create_log(company_id, "broadcast_created", {
        "broadcast_id": broadcast.get("id"),
        "title": body.title,
        "scheduled_at": scheduled_at,
    }, current_user["id"])

    return broadcast


@router.get("/{broadcast_id}")
async def get_broadcast(
    broadcast_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Detalhes de um broadcast."""
    sb = db.get_supabase()
    result = sb.table("broadcasts").select("*").eq("id", broadcast_id).maybe_single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Broadcast não encontrado")
    return result.data


@router.delete("/{broadcast_id}")
async def cancel_broadcast(
    broadcast_id: str,
    current_user: dict = Depends(get_admin_or_above),
):
    """Cancela um broadcast pendente."""
    sb = db.get_supabase()
    result = sb.table("broadcasts").select("*").eq("id", broadcast_id).maybe_single().execute()
    broadcast = result.data
    if not broadcast:
        raise HTTPException(status_code=404, detail="Broadcast não encontrado")

    if broadcast.get("status") not in ("pending",):
        raise HTTPException(status_code=400, detail=f"Não é possível cancelar broadcast com status '{broadcast['status']}'")

    sb.table("broadcasts").update({"status": "cancelled"}).eq("id", broadcast_id).execute()
    return {"status": "cancelled"}
