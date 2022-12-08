import asyncio
import json

import jieba
from fake_useragent import UserAgent
from loguru import logger
from playwright.async_api import async_playwright
from rearq import ReArq
from rearq.constants import JOB_TIMEOUT_UNLIMITED
from tortoise import Tortoise

from beauty import utils
from beauty.enums import Origin
from beauty.models import Collection, Picture
from beauty.origin.netbian import NetBian
from beauty.settings import settings
from beauty.third import meili
from beauty.third.minio import download_and_upload
from beauty.third.redis import Key, redis

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
                    pictures, update_fields=["description"], on_conflict=["origin_url"]
                )
        finally:
            await obj.close()

    return count


@rearq.task(cron="0 0 * * *")
async def get_origins():
    origins = utils.get_origins()
    for origin in origins.keys():
        await get_origin_pictures.delay(origin)


@rearq.task(cron="0 1 * * *")
async def get_tags():
    pictures = await Picture.filter().only("description")
    for picture in pictures:
        result = jieba.cut(picture.description)
        for word in result:
            if len(word) > 1:
                await redis.zincrby(Key.tags, 1, word)
    total = await redis.zcard(Key.tags)
    return await redis.zremrangebyrank(Key.tags, 0, total - 20)


@rearq.task(cron="0 3 * * *")
async def sync_pictures():
    limit = 10000
    offset = 0
    total = 0
    while True:
        pics = (
            await Picture.all()
            .order_by("id")
            .limit(limit)
            .offset(offset)
            .only("id", "description", "created_at")
        )
        if not pics:
            break
        total += len(pics)
        await meili.add_pictures(*pics)
        logger.success(f"Successfully save {len(pics)} pics, offset: {offset}")
        offset += limit
    return total


@rearq.task(cron="0 4 * * *")
async def sync_collections():
    limit = 10000
    offset = 0
    total = 0
    while True:
        collections = (
            await Collection.all()
            .order_by("id")
            .limit(limit)
            .offset(offset)
            .only("id", "title", "description")
        )
        if not collections:
            break
        total += len(collections)
        await meili.add_collections(*collections)
        logger.success(f"Successfully save {len(collections)} collections, offset: {offset}")
        offset += limit
    return total


@rearq.task(cron="*/20 * * * *")
async def refresh_cookies():
    picture = await Picture.filter(origin=Origin.netbian).only("origin_url").first()
    if not picture:
        return
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        user_agent = UserAgent().random
        context = await browser.new_context(user_agent=user_agent)
        page = await context.new_page()
        await page.goto(picture.origin_url)
        await page.reload()
        await asyncio.sleep(5)
        cookies = await context.cookies()
        if NetBian.is_valid_cookies(cookies):
            await redis.hset(
                Key.cookies,
                NetBian.origin.value,
                json.dumps(
                    {
                        "user_agent": user_agent,
                        "cookies": cookies,
                    }
                ),
            )
        return cookies


@rearq.task(cron="0 * * * *", job_timeout=JOB_TIMEOUT_UNLIMITED, run_with_lock=True)
async def download_pictures(concurrency: int = 10):
    sem = asyncio.Semaphore(concurrency)

    pictures = await Picture.filter(url=None).only("id", "origin", "origin_url")
    tasks = []
    for picture in pictures:
        tasks.append(
            asyncio.ensure_future(
                download_and_upload(sem, picture.pk, picture.origin, picture.origin_url)
            )
        )
    await asyncio.gather(*tasks)
    return len(pictures)
