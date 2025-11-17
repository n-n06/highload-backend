import redis.asyncio as redis
from typing import Any, Optional

from src.bootstrap.config import settings


class RedisClient:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        self.client = await redis.from_url(
            self.redis_url,
            encoding="utf8",
            decode_responses=True,
            max_connections=50,
        )

    async def disconnect(self) -> None:
        if self.client:
            await self.client.close()

    async def get(self, key: str) -> Optional[str]:
        if not self.client:
            raise RuntimeError("Redis client not connected")
        return await self.client.get(key)

    async def set(
        self, key: str, value: Any, ex: Optional[int] = None
    ) -> None:
        if not self.client:
            raise RuntimeError("Redis client not connected")
        await self.client.set(key, value, ex=ex)

    async def delete(self, *keys: str) -> int:
        if not self.client:
            raise RuntimeError("Redis client not connected")
        return await self.client.delete(*keys)

    async def exists(self, *keys: str) -> bool:
        if not self.client:
            raise RuntimeError("Redis client not connected")
        return await self.client.exists(*keys) > 0

    async def expire(self, key: str, time: int) -> bool:
        if not self.client:
            raise RuntimeError("Redis client not connected")
        return await self.client.expire(key, time)

    async def ttl(self, key: str) -> int:
        if not self.client:
            raise RuntimeError("Redis client not connected")
        return await self.client.ttl(key)

    async def flush(self) -> None:
        if not self.client:
            raise RuntimeError("Redis client not connected")
        await self.client.flushdb()


async def get_redis_client() -> RedisClient:
    client = RedisClient(str(settings.redis_url))
    await client.connect()
    return client
