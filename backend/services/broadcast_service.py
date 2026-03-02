"""
Serviço de broadcast - agendamento e envio em massa
"""
import asyncio
from datetime import datetime, timezone
from backend import database as db
from backend.services import evolution_service as evo


DELAY_BETWEEN_MESSAGES = 3  # segundos entre mensagens para evitar bloqueio


async def process_pending_broadcasts():
    """
    Chamado periodicamente pelo APScheduler.
    Busca broadcasts pendentes cujo scheduled_at já passou e os envia.
    """
    try:
        sb = db.get_supabase()
        now_iso = datetime.now(timezone.utc).isoformat()

        # Busca broadcasts pendentes prontos para envio
        result = sb.table("broadcasts") \
            .select("*, companies(evolution_instance, evolution_apikey)") \
            .eq("status", "pending") \
            .lte("scheduled_at", now_iso) \
            .execute()

        broadcasts = result.data or []

        for broadcast in broadcasts:
            await _send_broadcast(broadcast)

    except Exception as e:
        print(f"[Broadcast] Erro ao processar: {e}")


async def _send_broadcast(broadcast: dict):
    """Envia um broadcast para todos os contatos-alvo."""
    broadcast_id = broadcast.get("id")
    company_id = broadcast.get("company_id")
    content = broadcast.get("content", "")
    media_url = broadcast.get("media_url")
    media_type = broadcast.get("media_type")
    target_tags = broadcast.get("target_tags", [])
    target_phones = broadcast.get("target_phone_list", [])

    company_data = broadcast.get("companies", {})
    instance = company_data.get("evolution_instance", "")
    apikey = company_data.get("evolution_apikey", "")

    if not instance or not apikey:
        await _update_broadcast_status(broadcast_id, "failed")
        return

    # Marca como enviando
    await _update_broadcast_status(broadcast_id, "sending")

    # Busca contatos alvo
    contacts = await _get_target_contacts(company_id, target_tags, target_phones)

    sent = 0
    failed = 0

    for contact in contacts:
        try:
            phone = contact.get("phone", "")
            if not phone:
                continue

            if media_url and media_type:
                await evo.send_media_message(instance, phone, media_url, media_type, content, apikey=apikey)
            else:
                await evo.send_text_message(instance, phone, content, apikey=apikey)

            # Salva no histórico
            await db.save_message(company_id, contact.get("id"), "out", media_type or "text", content, media_url=media_url)
            sent += 1

        except Exception as e:
            print(f"[Broadcast] Erro ao enviar para {contact.get('phone')}: {e}")
            failed += 1

        # Delay anti-bloqueio
        await asyncio.sleep(DELAY_BETWEEN_MESSAGES)

    # Atualiza status final
    sb = db.get_supabase()
    sb.table("broadcasts").update({
        "status": "completed",
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "sent_count": sent,
        "failed_count": failed,
    }).eq("id", broadcast_id).execute()

    await db.create_log(company_id, "broadcast_completed", {
        "broadcast_id": broadcast_id,
        "sent": sent,
        "failed": failed,
    })


async def _get_target_contacts(company_id: str, target_tags: list, target_phones: list) -> list:
    """Busca contatos pelo critério do broadcast."""
    sb = db.get_supabase()

    if target_phones:
        result = sb.table("contacts") \
            .select("id, phone") \
            .eq("company_id", company_id) \
            .in_("phone", target_phones) \
            .execute()
        return result.data or []

    if target_tags:
        # Busca contatos com qualquer uma das tags
        result = sb.table("contacts") \
            .select("id, phone, contact_tags(tag_id)") \
            .eq("company_id", company_id) \
            .execute()
        contacts = result.data or []
        # Filtra pelo lado Python pois Supabase não tem filtro direto em tabela de junção
        return [c for c in contacts if any(
            ct.get("tag_id") in target_tags for ct in c.get("contact_tags", [])
        )]

    # Sem filtro = todos os contatos da empresa
    result = sb.table("contacts").select("id, phone").eq("company_id", company_id).execute()
    return result.data or []


async def _update_broadcast_status(broadcast_id: str, status: str):
    try:
        sb = db.get_supabase()
        sb.table("broadcasts").update({"status": status}).eq("id", broadcast_id).execute()
    except Exception as e:
        print(f"[Broadcast] Erro ao atualizar status: {e}")
