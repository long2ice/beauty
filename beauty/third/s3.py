import aioboto3

from beauty.settings import settings


async def upload_file(object_name: str, content_type: str, data: bytes):
    session = aioboto3.Session()
    async with session.client(
        "s3",
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION,
        endpoint_url=("https://" if settings.S3_SECURE else "http://") + settings.S3_ENDPOINT,
    ) as s3:
        return await s3.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=object_name,
            Body=data,
            ContentType=content_type,
            CacheControl="max-age=31536000",
        )


def format_url(url: str):
    return f"{settings.S3_URL}/{settings.S3_BUCKET_NAME}/{url}"
