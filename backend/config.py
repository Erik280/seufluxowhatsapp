from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "WhatsApp Atendimento SaaS"
    APP_ENV: str = "development"
    APP_SECRET_KEY: str = "super_secret_jwt_key"
    APP_PORT: int = 8000
    SUPERADMIN_ID: str = "fd7e3273-4e7a-43df-80ed-1d00591cd656"

    # Supabase
    SUPABASE_URL: str = "http://127.0.0.1:54321"
    SUPABASE_KEY: str = ""
    SUPABASE_SECRET: str = ""
    DATABASE_URL: str = ""

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # MinIO
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = ""
    MINIO_SECRET_KEY: str = ""
    MINIO_BUCKET: str = "whatsapp-storage"
    MINIO_SECURE: bool = False
    MINIO_PUBLIC_URL: str = "http://minio:9000/whatsapp-storage"

    # Evolution API
    EVOLUTION_API_URL: str = "http://evolution:8080"
    EVOLUTION_API_KEY: str = ""

    # Frontend
    FRONTEND_PORT: int = 8080
    BACKEND_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
