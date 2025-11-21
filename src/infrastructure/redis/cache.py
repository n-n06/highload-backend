import json
import functools
from typing import Any, Callable, Optional, TypeVar
from inspect import iscoroutinefunction

from src.infrastructure.redis.client import RedisClient
from src.infrastructure.redis.utils import make_key

T = TypeVar("T")


def cache(
    ttl: int = 300,
    prefix: str = "cache",
):

    def decorator(func: Callable) -> Callable:
        if not iscoroutinefunction(func):
            raise ValueError(f"@cache decorator only works with async functions. Got {func}")

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            redis_client: Optional[RedisClient] = kwargs.pop("_redis_client", None)

            if not redis_client:
                return await func(*args, **kwargs)

            cache_key = make_key(prefix, func.__name__, *args, **kwargs)


            try:
                cached_value = await redis_client.get(cache_key)
                if cached_value is not None:
                    return json.loads(cached_value)
            except Exception as e:
                print(f"Cache read error for {cache_key}: {e}")


            result = await func(*args, **kwargs)


            try:
                await redis_client.set(
                    cache_key,
                    json.dumps(result, default=str),
                    ex=ttl
                )
            except Exception as e:
                print(f"Cache write error for {cache_key}: {e}")

            return result

        return wrapper
    return decorator


def invalidate_cache(
    prefix: str,
    func_name: Optional[str] = None,
):

    def decorator(func: Callable) -> Callable:
        if not iscoroutinefunction(func):
            raise ValueError(f"@invalidate_cache decorator only works with async functions. Got {func}")

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            redis_client: Optional[RedisClient] = kwargs.pop("_redis_client", None)

            result = await func(*args, **kwargs)


            if redis_client:
                try:

                    if func_name:
                        key = make_key(prefix, func_name, *args, **kwargs)
                        await redis_client.delete(key)
                except Exception as e:
                    print(f"Cache invalidation error: {e}")

            return result

        return wrapper
    return decorator


class CacheManager:

    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client

    async def get_or_set(
        self,
        key: str,
        func: Callable,
        ttl: int = 300,
    ) -> Any:

        try:
            cached = await self.redis_client.get(key)
            if cached is not None:
                return json.loads(cached)
        except Exception as e:
            print(f"Cache read error: {e}")

        result = await func()

        try:
            await self.redis_client.set(
                key,
                json.dumps(result, default=str),
                ex=ttl
            )
        except Exception as e:
            print(f"Cache write error: {e}")

        return result

    async def invalidate(self, *keys: str) -> None:
        await self.redis_client.delete(*keys)

    async def invalidate_pattern(self, pattern: str) -> None:

        if not self.redis_client.client:
            return

        keys = await self.redis_client.client.keys(pattern)
        if keys:
            await self.redis_client.delete(*keys)
