from io import BytesIO

from minio import Minio

from beauty.settings import settings
from beauty.utils import run_async

client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE,
)


async def upload_file(object_name: str, content_type: str, data: BytesIO):
    return await run_async(
        client.put_object,
        settings.MINIO_BUCKET_NAME,
        object_name,
        data,
        data.getbuffer().nbytes,
        content_type,
        {
            "Cache-Control": "max-age=31536000",
        },
    )


def format_url(url: str):
    return f"{settings.MINIO_URL}/{settings.MINIO_BUCKET_NAME}/{url}"
