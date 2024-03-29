import hashlib
import json

import httpx
import jieba
from loguru import logger
from rearq import ReArq
from rearq.constants import JOB_TIMEOUT_UNLIMITED
from tortoise import Tortoise
from tortoise.expressions import Q

from beauty import constants, utils
from beauty.enums import Origin, PictureCategory
from beauty.models import Picture
from beauty.origin.netbian import NetBian
from beauty.settings import settings
from beauty.third.redis import Key, redis
from beauty.third.s3 import upload_file

rearq = ReArq(
    db_url=settings.DB_URL,
    redis_url=settings.REDIS_URL,
    keep_job_days=7,
    job_retry=0,
    job_timeout=60 * 30,
    expire=3 * 60,
    trace_exception=settings.DEBUG,
)


@rearq.on_startup
async def startup():
    await Tortoise.init(
        db_url=settings.DB_URL,
        modules={"models": ["beauty.models"]},
    )
    await Tortoise.generate_schemas()


@rearq.on_shutdown
async def shutdown():
    await Tortoise.close_connections()


@rearq.task(job_timeout=JOB_TIMEOUT_UNLIMITED)
async def get_origin_pictures(origin: str):
    origins = utils.get_origin(Origin(origin))
    count = 0
    for cls in origins:
        obj = cls()
        try:
            async for pictures in obj.run():
                count += len(pictures)
                await Picture.bulk_create(
                    pictures,
                    update_fields=["description", "category"],
                    on_conflict=["origin_url"],
                )
        finally:
            await obj.close()

    return count


@rearq.task(cron="0 1 * * *")
async def get_origins():
    origins = utils.get_origins()
    for origin in origins.keys():
        await get_origin_pictures.delay(origin)


@rearq.task(cron="0 1 * * *")
async def get_tags():
    if settings.is_auditing:
        pictures = await Picture.filter(~Q(category=PictureCategory.beauty)).only("description")
    else:
        pictures = await Picture.filter(category=PictureCategory.beauty).only("description")
    for picture in pictures:
        result = jieba.cut(picture.description)
        for word in result:
            if len(word) > 1:
                await redis.zincrby(Key.tags_tmp, 1, word)

    total = await redis.zcard(Key.tags_tmp)
    async with redis.pipeline() as pipe:
        await pipe.zremrangebyrank(Key.tags_tmp, 0, total - 20)
        pipe.delete(Key.tags)
        pipe.rename(Key.tags_tmp, Key.tags)
        await pipe.execute()
    return await redis.zrange(Key.tags, 0, -1)


async def download_and_upload(pk: int, origin: Origin, url: str):
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
            await upload_file(objectname, content_type, resp.content)
            await Picture.filter(id=pk).update(url=objectname)
            return objectname
        elif resp.status_code == 404:
            await Picture.filter(id=pk).delete()
        elif resp.status_code == 503 and origin == Origin.netbian:
            await NetBian().refresh_cookies()
        else:
            logger.error(f"Download picture failed, url: {url}")


@rearq.task(cron="0 * * * *", job_timeout=JOB_TIMEOUT_UNLIMITED, run_with_lock=True)
async def download_pictures():
    pictures = await Picture.filter(url=None).only("id", "origin", "origin_url")
    for picture in pictures:
        await download_and_upload(picture.pk, picture.origin, picture.origin_url)
    return len(pictures)
