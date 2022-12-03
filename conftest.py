import asyncio

import pytest
from tortoise import Tortoise

from beauty import settings


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="session", autouse=True)
async def init_db():
    await Tortoise.init(config=settings.TORTOISE_ORM)
    yield
    await Tortoise.close_connections()
