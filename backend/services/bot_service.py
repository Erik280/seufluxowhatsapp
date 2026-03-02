"""
Serviço de processamento de fluxos de bot
"""
import asyncio
from backend import database as db
from backend.services import evolution_service as evo


async def process_message(contact: dict, message_text: str, company: dict) -> bool:
    """
    Processa uma mensagem recebida e verifica se algum flow é acionado.
    Retorna True se o bot respondeu, False caso contrário.
    """
    instance = company.get("evolution_instance", "")
    apikey = company.get("evolution_apikey", "")
    phone = contact.get("phone", "")
    company_id = company.get("id", "")

    if not instance or not apikey or not phone:
        return False

    # Busca flows ativos
    flows = await db.get_active_flows(company_id)
    if not flows:
        return False

    message_lower = message_text.lower().strip()

    for flow in flows:
        if _message_matches_flow(message_lower, message_text, flow):
            # Aciona o flow
            await _execute_flow(flow, phone, instance, apikey, company_id, contact.get("id"))
            return True

    return False


def _message_matches_flow(message_lower: str, message_original: str, flow: dict) -> bool:
    """Verifica se a mensagem corresponde ao gatilho do flow."""
    keyword = flow.get("trigger_keyword", "")
    match_type = flow.get("match_type", "contains")

    if match_type == "exact":
        # Suporta múltiplas palavras-chave separadas por vírgula
        keywords = [k.strip().lower() for k in keyword.split(",")]
        return message_lower in keywords

    elif match_type == "contains":
        keywords = [k.strip().lower() for k in keyword.split(",")]
        return any(kw in message_lower for kw in keywords)

    elif match_type == "starts_with":
        keywords = [k.strip().lower() for k in keyword.split(",")]
        return any(message_lower.startswith(kw) for kw in keywords)

    elif match_type == "regex":
        import re
        try:
            return bool(re.search(keyword, message_original, re.IGNORECASE))
        except re.error:
            return False

    return False


async def _execute_flow(flow: dict, phone: str, instance: str, apikey: str, company_id: str, contact_id: str):
    """Executa os steps do flow em sequência com delay."""
    steps = sorted(flow.get("flow_steps", []), key=lambda s: s.get("position", 0))

    for step in steps:
        delay = step.get("delay_seconds", 2)
        show_typing = step.get("typing_indicator", True)
        message_type = step.get("message_type", "text")
        content = step.get("content", "")
        media_url = step.get("media_url", "")

        # Delay antes de enviar
        if delay > 0:
            await asyncio.sleep(delay)

        # Indicador de digitação
        if show_typing:
            await evo.send_typing(instance, phone, duration_ms=delay * 1000, apikey=apikey)
            await asyncio.sleep(1.5)

        # Envia a mensagem
        if message_type == "text" and content:
            await evo.send_text_message(instance, phone, content, apikey=apikey)
            # Salva no histórico
            await db.save_message(company_id, contact_id, "out", "text", content)

        elif message_type in ("image", "video", "document") and (media_url or content):
            url = media_url or ""
            caption = content if media_url else ""
            await evo.send_media_message(instance, phone, url, message_type, caption, apikey=apikey)
            await db.save_message(company_id, contact_id, "out", message_type, caption, media_url=url)

        elif message_type == "audio" and media_url:
            await evo.send_audio_message(instance, phone, media_url, apikey=apikey)
            await db.save_message(company_id, contact_id, "out", "audio", "", media_url=media_url)
