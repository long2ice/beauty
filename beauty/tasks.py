import asyncio
import json

from fake_useragent import UserAgent
from loguru import logger
from playwright.async_api import async_playwright
from rearq import ReArq
from rearq.constants import JOB_TIMEOUT_UNLIMITED
from tortoise import Tortoise

from beauty import meili, utils
from beauty.enums import Origin
from beauty.models import Collection, Picture
from beauty.origin.netbian import NetBian
from beauty.redis import Key, redis
from beauty.settings import settings

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
    cls = utils.get_origin(Origin(origin))
    obj = cls()
    count = 0
    try:
        async for pictures in obj.run():
            count += len(pictures)
            await Picture.bulk_create(
                pictures, update_fields=["description"], on_conflict=["url"]
            )
    finally:
        await obj.close()

    return count


@rearq.task(cron="0 0 * * *")
async def get_origins():
    origins = utils.get_origins()
    for origin in origins.keys():
        await get_origin_pictures.delay(origin)


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
            .only("id", "description")
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
        logger.success(
            f"Successfully save {len(collections)} collections, offset: {offset}"
        )
        offset += limit
    return total


@rearq.task(cron="*/20 * * * *")
async def refresh_cookies():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        user_agent = UserAgent().random
        context = await browser.new_context(user_agent=user_agent)
        page = await context.new_page()
        await page.goto(NetBian.homepage)
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
