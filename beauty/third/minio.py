import asyncio
import hashlib
import json
from io import BytesIO

import httpx
from loguru import logger
from minio import Minio

from beauty import constants
from beauty.enums import Origin
from beauty.models import Picture
from beauty.settings import settings
from beauty.third import meili
from beauty.third.redis import Key, redis
from beauty.utils import run_async

client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE,
)


async def init():
    await run_async(
        client.set_bucket_policy,
        settings.MINIO_BUCKET_NAME,
        "",
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


async def download_and_upload(sem: asyncio.Semaphore, pk: int, origin: Origin, url: str):
    async with sem:
        headers = {}
        httpx_cookies = None
        if origin == Origin.netbian:
            cookies = await redis.hget(Key.cookies, origin.value)  # type: ignore
            if cookies:
                cookies = json.loads(cookies)
                user_agent = cookies.get("user_agent")
                cookies = cookies.get("cookies")
                headers["User-Agent"] = user_agent
                httpx_cookies = httpx.Cookies()
                for cookie in cookies:
                    httpx_cookies.set(cookie["name"], cookie["value"])
        async with httpx.AsyncClient(headers=headers, cookies=httpx_cookies, timeout=30) as http:
            try:
                resp = await http.get(url)
            except Exception as e:
                logger.error(f"download {url} error: {e}")
                return
            if resp.status_code == 200:
                objectname = (
                    constants.PICTURES
                    + "/"
                    + (hashlib.md5(url.encode()).hexdigest() + "." + url.split(".")[-1])
                )
                content_type = resp.headers.get("Content-Type")
                await upload_file(objectname, content_type, BytesIO(resp.content))
                await Picture.filter(id=pk).update(url=objectname)
                return objectname
            elif resp.status_code == 404:
                await Picture.filter(id=pk).delete()
                await meili.delete_pictures(pk)
            else:
                logger.error(f"Download picture failed, url: {url}")
