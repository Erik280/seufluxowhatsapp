"""
SuperAdmin - Visão global de empresas, usuários e logs
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from backend.models.schemas import CompanyCreate, CompanyUpdate, UserCreate
from backend.routers.auth import get_superadmin, get_current_user, hash_password
from backend import database as db

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/companies")
async def list_companies(
    _: dict = Depends(get_superadmin),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
):
    """SuperAdmin: lista todas as empresas."""
    sb = db.get_supabase()
    result = sb.table("companies").select("*").order("created_at", desc=True).range(offset, offset + limit - 1).execute()
    return result.data or []


@router.post("/companies")
async def create_company(
    body: CompanyCreate,
    current_user: dict = Depends(get_superadmin),
):
    """SuperAdmin: cria uma nova empresa."""
    sb = db.get_supabase()
    result = sb.table("companies").insert(body.model_dump(exclude_none=True)).execute()
    company = result.data[0] if result.data else {}
    await db.create_log(None, "company_created", {"name": body.name}, current_user["id"])
    return company


@router.put("/companies/{company_id}")
async def update_company(
    company_id: str,
    body: CompanyUpdate,
    _: dict = Depends(get_superadmin),
):
    """SuperAdmin: atualiza dados de uma empresa."""
    sb = db.get_supabase()
    result = sb.table("companies").update(body.model_dump(exclude_none=True)).eq("id", company_id).execute()
    return result.data[0] if result.data else {}


@router.get("/users")
async def list_all_users(
    _: dict = Depends(get_superadmin),
    company_id: str = Query(default=""),
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0, ge=0),
):
    """SuperAdmin: lista todos os usuários."""
    sb = db.get_supabase()
    query = sb.table("users").select("id, full_name, email, role, is_online, created_at, company_id, companies(name)")
    if company_id:
        query = query.eq("company_id", company_id)
    result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
    return result.data or []


@router.post("/users")
async def create_user(
    body: UserCreate,
    current_user: dict = Depends(get_superadmin),
):
    """SuperAdmin: cria um usuário em qualquer empresa."""
    sb = db.get_supabase()
    result = sb.table("users").insert({
        "company_id": body.company_id,
        "full_name": body.full_name,
        "email": body.email,
        "password_hash": hash_password(body.password),
        "role": body.role.value,
    }).execute()
    user = result.data[0] if result.data else {}
    user.pop("password_hash", None)
    await db.create_log(body.company_id, "user_created", {"email": body.email}, current_user["id"])
    return user


@router.get("/logs")
async def get_system_logs(
    _: dict = Depends(get_superadmin),
    company_id: str = Query(default=""),
    action: str = Query(default=""),
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0, ge=0),
):
    """SuperAdmin: logs globais do sistema."""
    sb = db.get_supabase()
    query = sb.table("system_logs").select("*, companies(name), users(full_name, email)")
    if company_id:
        query = query.eq("company_id", company_id)
    if action:
        query = query.eq("action", action)
    result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
    return result.data or []


@router.get("/stats")
async def get_global_stats(_: dict = Depends(get_superadmin)):
    """SuperAdmin: estatísticas globais do sistema."""
    sb = db.get_supabase()
    companies = sb.table("companies").select("id", count="exact").execute()
    users = sb.table("users").select("id", count="exact").execute()
    contacts = sb.table("contacts").select("id", count="exact").execute()
    messages = sb.table("messages_history").select("id", count="exact").execute()
    broadcasts = sb.table("broadcasts").select("id", count="exact").execute()

    return {
        "total_companies": companies.count or 0,
        "total_users": users.count or 0,
        "total_contacts": contacts.count or 0,
        "total_messages": messages.count or 0,
        "total_broadcasts": broadcasts.count or 0,
    }


# --- Rotas para tags (admin da empresa) ---
@router.get("/tags")
async def list_tags(current_user: dict = Depends(get_current_user)):
    """Lista tags da empresa do usuário."""
    company_id = current_user.get("company_id")
    sb = db.get_supabase()
    result = sb.table("tags").select("*").eq("company_id", company_id).execute()
    return result.data or []


@router.post("/tags")
async def create_tag(
    body: dict,
    current_user: dict = Depends(get_current_user),
):
    """Cria uma nova tag para a empresa."""
    company_id = current_user.get("company_id")
    sb = db.get_supabase()
    result = sb.table("tags").insert({
        "company_id": company_id,
        "name": body.get("name", ""),
        "color": body.get("color", "#3498db"),
    }).execute()
    return result.data[0] if result.data else {}


@router.delete("/tags/{tag_id}")
async def delete_tag(
    tag_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Remove uma tag."""
    sb = db.get_supabase()
    sb.table("tags").delete().eq("id", tag_id).execute()
    return {"status": "deleted"}
