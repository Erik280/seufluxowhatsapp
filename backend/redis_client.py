import redis.asyncio as aioredis
from backend.config import settings

_redis_pool = None

CHAT_STATUS_TTL = 86400 * 7  # 7 dias


async def get_redis() -> aioredis.Redis:
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )
    return _redis_pool


async def get_chat_status(phone: str, company_id: str) -> str:
    """Retorna o status do chat: 'bot', 'human' ou 'paused'"""
    try:
        r = await get_redis()
        key = f"chat_status:{company_id}:{phone}"
        status = await r.get(key)
        return status or "bot"
    except Exception:
        return "bot"


async def set_chat_status(phone: str, company_id: str, status: str, ttl: int = CHAT_STATUS_TTL):
    """Define o status do chat no Redis"""
    try:
        r = await get_redis()
        key = f"chat_status:{company_id}:{phone}"
        await r.setex(key, ttl, status)
    except Exception as e:
        print(f"[Redis] Erro ao definir status: {e}")


async def delete_chat_status(phone: str, company_id: str):
    """Remove o status – volta para bot por padrão"""
    try:
        r = await get_redis()
        key = f"chat_status:{company_id}:{phone}"
        await r.delete(key)
    except Exception as e:
        print(f"[Redis] Erro ao deletar status: {e}")


async def set_typing(phone: str, company_id: str, duration: int = 5):
    """Marca que o bot está digitando"""
    try:
        r = await get_redis()
        key = f"typing:{company_id}:{phone}"
        await r.setex(key, duration, "1")
    except Exception:
        pass


async def close_redis():
    global _redis_pool
    if _redis_pool:
        await _redis_pool.close()
        _redis_pool = None
