from minio import Minio
from minio.error import S3Error
from io import BytesIO
import uuid
import httpx
from backend.config import settings

_minio_client: Minio | None = None


def get_minio() -> Minio:
    global _minio_client
    if _minio_client is None:
        _minio_client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        # Garante que o bucket existe
        try:
            if not _minio_client.bucket_exists(settings.MINIO_BUCKET):
                _minio_client.make_bucket(settings.MINIO_BUCKET)
        except S3Error as e:
            print(f"[MinIO] Aviso ao verificar bucket: {e}")
    return _minio_client


async def upload_media(file_bytes: bytes, extension: str, content_type: str) -> str:
    """Upload de mídia para MinIO. Retorna URL pública."""
    try:
        client = get_minio()
        object_name = f"media/{uuid.uuid4()}.{extension}"
        client.put_object(
            bucket_name=settings.MINIO_BUCKET,
            object_name=object_name,
            data=BytesIO(file_bytes),
            length=len(file_bytes),
            content_type=content_type,
        )
        return f"{settings.MINIO_PUBLIC_URL}/{object_name}"
    except Exception as e:
        print(f"[MinIO] Erro no upload: {e}")
        return ""


async def download_and_upload_media(url: str, content_type: str = "application/octet-stream") -> str:
    """Baixa mídia de uma URL externa e faz upload no MinIO."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url)
            response.raise_for_status()

        content_type_header = response.headers.get("content-type", content_type)
        # Determina extensão pelo content-type
        ext_map = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
            "audio/ogg": "ogg",
            "audio/mpeg": "mp3",
            "video/mp4": "mp4",
            "application/pdf": "pdf",
        }
        extension = ext_map.get(content_type_header.split(";")[0].strip(), "bin")
        return await upload_media(response.content, extension, content_type_header)
    except Exception as e:
        print(f"[MinIO] Erro ao baixar/fazer upload: {e}")
        return url  # Retorna URL original como fallback


def get_presigned_url(object_name: str, expires_hours: int = 24) -> str:
    """Gera URL com assinatura temporária para objetos privados."""
    try:
        from datetime import timedelta
        client = get_minio()
        return client.presigned_get_object(
            bucket_name=settings.MINIO_BUCKET,
            object_name=object_name,
            expires=timedelta(hours=expires_hours),
        )
    except Exception as e:
        print(f"[MinIO] Erro ao gerar URL assinada: {e}")
        return ""
