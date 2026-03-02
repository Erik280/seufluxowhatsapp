from supabase import create_client, Client
from backend.config import settings

_supabase_client: Client | None = None


def get_supabase() -> Client:
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SECRET  # Service role key para bypass de RLS no backend
        )
    return _supabase_client


# Helper: busca contato por telefone e empresa
async def get_contact_by_phone(company_id: str, phone: str) -> dict | None:
    sb = get_supabase()
    result = sb.table("contacts").select("*").eq("company_id", company_id).eq("phone", phone).maybe_single().execute()
    return result.data


# Helper: upsert contato
async def upsert_contact(company_id: str, phone: str, data: dict = {}) -> dict:
    sb = get_supabase()
    payload = {"company_id": company_id, "phone": phone, **data}
    result = sb.table("contacts").upsert(payload, on_conflict="company_id,phone").execute()
    return result.data[0] if result.data else {}


# Helper: salva mensagem no histórico
async def save_message(company_id: str, contact_id: str, direction: str, message_type: str, content: str, media_url: str | None = None, evolution_message_id: str | None = None) -> dict:
    sb = get_supabase()
    result = sb.table("messages_history").insert({
        "company_id": company_id,
        "contact_id": contact_id,
        "direction": direction,
        "message_type": message_type,
        "content": content,
        "media_url": media_url,
        "evolution_message_id": evolution_message_id,
    }).execute()
    return result.data[0] if result.data else {}


# Helper: busca empresa por ID
async def get_company(company_id: str) -> dict | None:
    sb = get_supabase()
    result = sb.table("companies").select("*").eq("id", company_id).maybe_single().execute()
    return result.data


# Helper: busca flows ativos por empresa
async def get_active_flows(company_id: str) -> list:
    sb = get_supabase()
    result = sb.table("chat_flows").select("*, flow_steps(*)").eq("company_id", company_id).eq("is_active", True).order("priority", desc=True).execute()
    return result.data or []


# Helper: log de sistema
async def create_log(company_id: str | None, action: str, details: dict = {}, user_id: str | None = None):
    try:
        sb = get_supabase()
        sb.table("system_logs").insert({
            "company_id": company_id,
            "user_id": user_id,
            "action": action,
            "details": details,
        }).execute()
    except Exception:
        pass  # Logs não devem quebrar o fluxo principal
