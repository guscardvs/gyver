from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Callable
from typing import Literal
from typing import Optional
from typing import TypeVar
from typing import Union

import redis
from redis import asyncio as aioredis

from gyver.config import from_config
from gyver.exc import CacheMiss
from gyver.utils import json
from gyver.utils import lazyfield

from .config import CacheConfig
from .interface import AsyncCacheInterface
from .interface import CacheInterface
from .utils import make_uri

T = TypeVar("T")


class AsyncRedisWrapper(AsyncCacheInterface):
    def __init__(self, cache_config: Optional[CacheConfig] = None) -> None:
        self._config = cache_config or from_config(CacheConfig)

    def _pool(self):
        return aioredis.ConnectionPool.from_url(make_uri(self._config))

    @lazyfield
    def _instance(self):
        return aioredis.Redis(connection_pool=self._pool())

    async def get(self, name: str, cast: Callable[[Any], T] = json.loads) -> T:
        response = await self._instance.get(name)
        if response is None:
            raise CacheMiss
        return cast(response)

    async def set(
        self,
        name: str,
        value: Any,
        expires_at: Union[datetime, Literal[-1]],
        dumps: Callable[[Any], str] = json.dumps,
    ) -> None:
        expiration = None if expires_at == -1 else expires_at
        await self._instance.set(
            name,
            dumps(value),
            ex=expiration and expiration - datetime.now(timezone.utc),
        )

    async def map_get(
        self, map_name: str, name: str, cast: Callable[[Any], T] = json.loads
    ) -> T:
        try:
            response = await self._instance.hget(map_name, name)
        except aioredis.RedisError:
            raise CacheMiss from None
        else:
            if response is None:
                raise CacheMiss
            return cast(response)

    async def map_set(
        self,
        map_name: str,
        name: str,
        value: Any,
        dumps: Callable[[Any], str] = json.dumps,
    ) -> None:
        await self._instance.hset(
            map_name,
            name,
            dumps(value),
        )

    async def delete(self, name: str, map_name: Optional[str] = None) -> None:
        if map_name is None:
            await self._instance.delete(name)
        else:
            await self._instance.hdel(map_name, name)


class RedisWrapper(CacheInterface):
    def __init__(self, cache_config: Optional[CacheConfig] = None) -> None:
        self._config = cache_config or from_config(CacheConfig)

    def _pool(self):
        return redis.ConnectionPool.from_url(make_uri(self._config))

    @lazyfield
    def _instance(self):
        return redis.Redis(connection_pool=self._pool())

    def get(self, name: str, cast: Callable[[Any], T] = json.loads) -> T:
        response = self._instance.get(name)
        if response is None:
            raise CacheMiss
        return cast(response.decode("utf-8"))

    def set(
        self,
        name: str,
        value: Any,
        expires_at: Union[datetime, Literal[-1]],
        dumps: Callable[[Any], str] = json.dumps,
    ) -> None:
        expiration = None if expires_at == -1 else expires_at
        self._instance.set(
            name,
            dumps(value),
            ex=expiration and expiration - datetime.now(timezone.utc),
        )

    def map_get(
        self, map_name: str, name: str, cast: Callable[[Any], T] = json.loads
    ) -> T:
        try:
            response = self._instance.hget(map_name, name)
        except aioredis.RedisError:
            raise CacheMiss from None
        else:
            if response is None:
                raise CacheMiss
            return cast(response.decode("utf-8"))

    def map_set(
        self,
        map_name: str,
        name: str,
        value: Any,
        dumps: Callable[[Any], str] = json.dumps,
    ) -> None:
        self._instance.hset(
            map_name,
            name,
            dumps(value),
        )

    def delete(self, name: str, map_name: Optional[str] = None) -> None:
        if map_name is None:
            self._instance.delete(name)
        else:
            self._instance.hdel(map_name, name)
