from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings


_client: AsyncIOMotorClient | None = None


def get_mongo_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongo_dsn)
    return _client


def get_analytics_db():
    return get_mongo_client()[settings.MONGO_DB]

