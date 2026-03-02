"""
Serviço de mídia - download e upload
"""
from backend.minio_client import download_and_upload_media, upload_media
import httpx


async def process_incoming_media(media_url: str, content_type: str = "application/octet-stream", apikey: str = None) -> str:
    """
    Baixa mídia recebida via Evolution API e faz re-upload no MinIO.
    Retorna a URL pública no MinIO.
    """
    try:
        headers = {}
        if apikey:
            headers["apikey"] = apikey

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(media_url, headers=headers)
            response.raise_for_status()

        ct = response.headers.get("content-type", content_type).split(";")[0].strip()
        ext_map = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
            "image/gif": "gif",
            "audio/ogg": "ogg",
            "audio/mpeg": "mp3",
            "audio/aac": "aac",
            "video/mp4": "mp4",
            "application/pdf": "pdf",
        }
        ext = ext_map.get(ct, "bin")
        return await upload_media(response.content, ext, ct)

    except Exception as e:
        print(f"[Media] Erro ao processar mídia: {e}")
        return media_url  # Fallback: retorna URL original
