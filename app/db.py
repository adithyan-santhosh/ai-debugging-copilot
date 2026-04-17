import logging
from motor.motor_asyncio import AsyncIOMotorClient
import asyncpg
from .config import get_settings

settings = get_settings()
log = logging.getLogger("app.db")

postgres_pool = None
mongo_client: AsyncIOMotorClient | None = None


async def connect_postgres():
    global postgres_pool
    if postgres_pool is None:
        postgres_pool = await asyncpg.create_pool(dsn=settings.pg_dsn)
        log.info("Connected to PostgreSQL")
    return postgres_pool


async def connect_mongo():
    global mongo_client
    if mongo_client is None:
        mongo_client = AsyncIOMotorClient(settings.mongo_uri)
        log.info("Connected to MongoDB")
    return mongo_client


async def close_db_connections():
    global postgres_pool, mongo_client
    if postgres_pool is not None:
        await postgres_pool.close()
        postgres_pool = None
    if mongo_client is not None:
        mongo_client.close()
        mongo_client = None
