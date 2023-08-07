from redis import asyncio

from src.config import REDIS_HOST, REDIS_PORT

pool = asyncio.ConnectionPool.from_url(f'redis://{REDIS_HOST}:{REDIS_PORT}')


async def get_async_redis():
    asyncio_redis = await asyncio.Redis(connection_pool=pool)
    try:
        yield asyncio_redis
    finally:
        await asyncio_redis.close()
