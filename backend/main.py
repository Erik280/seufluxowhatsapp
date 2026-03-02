"""
FastAPI Main - Entrypoint do backend
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from backend.config import settings
from backend.routers import webhook, auth, contacts, messages, broadcasts, admin
from backend.redis_client import get_redis, close_redis
from backend.minio_client import get_minio
from backend.services.broadcast_service import process_pending_broadcasts

# Scheduler global para broadcasts
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup e shutdown do servidor."""
    print(f"🚀 Iniciando {settings.APP_NAME}...")

    # Conecta Redis
    try:
        redis = await get_redis()
        await redis.ping()
        print("✅ Redis conectado")
    except Exception as e:
        print(f"⚠️  Redis não disponível: {e}")

    # Conecta MinIO
    try:
        get_minio()
        print("✅ MinIO conectado")
    except Exception as e:
        print(f"⚠️  MinIO não disponível: {e}")

    # Inicia scheduler de broadcasts (verifica a cada minuto)
    scheduler.add_job(
        process_pending_broadcasts,
        trigger="interval",
        minutes=1,
        id="broadcast_processor",
        name="Processor de Broadcasts",
        replace_existing=True,
    )
    scheduler.start()
    print("✅ Scheduler de broadcasts iniciado")

    yield  # Servidor rodando

    # Shutdown
    scheduler.shutdown()
    await close_redis()
    print("👋 Servidor encerrado")


# ============================================================
# APP FastAPI
# ============================================================
app = FastAPI(
    title="WhatsApp Atendimento SaaS API",
    description="API de atendimento multicanal WhatsApp com suporte a Bot + Humano",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS - Permite frontend Flet e desenvolvimento local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restringir para domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# ROUTERS
# ============================================================
app.include_router(auth.router)
app.include_router(webhook.router)
app.include_router(contacts.router)
app.include_router(messages.router)
app.include_router(broadcasts.router)
app.include_router(admin.router)


# ============================================================
# ENDPOINTS UTILITÁRIOS
# ============================================================
@app.get("/", tags=["Health"])
async def root():
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Verificação de saúde do sistema."""
    redis_ok = False
    try:
        r = await get_redis()
        await r.ping()
        redis_ok = True
    except Exception:
        pass

    return {
        "status": "healthy" if redis_ok else "degraded",
        "redis": "connected" if redis_ok else "disconnected",
        "scheduler": "running" if scheduler.running else "stopped",
    }
