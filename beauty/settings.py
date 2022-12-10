from typing import Optional

import sentry_sdk
from pydantic import BaseSettings
from sentry_sdk.integrations.redis import RedisIntegration

JWT_ALGORITHM = "HS256"


class Settings(BaseSettings):
    DEBUG: bool = False
    MEILI_URL: str
    MEILI_MASTER_KEY: Optional[str]
    DB_URL: str
    REDIS_URL: str
    API_SECRET: str
    SECRET: str
    ENV = "production"
    SENTRY_DSN: Optional[str]
    WECHAT_APP_ID: str
    WECHAT_APP_SECRET: str
    CACHE_EXPIRE_SECONDS: int = 60
    MINIO_ENDPOINT: str
    MINIO_URL: str
    MINIO_BUCKET_NAME: str = "beauty"
    MINIO_SECURE: bool = False
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str

    class Config:
        env_file = ".env"

    @property
    def is_auditing(self) -> bool:
        return self.ENV == "auditing"


settings = Settings()
TORTOISE_ORM = {
    "apps": {
        "models": {
            "models": ["beauty.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "connections": {"default": settings.DB_URL},
}
sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.ENV,
    integrations=[RedisIntegration()],
    traces_sample_rate=1.0,
)
