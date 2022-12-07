from enum import Enum

import redis.asyncio as redis

from beauty.settings import settings

redis = redis.from_url(settings.REDIS_URL, decode_responses=True)  # type:ignore


class Key(str, Enum):
    keywords = "keywords"
    cookies = "cookies"
    tags = "tags"
