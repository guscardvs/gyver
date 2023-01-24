import typing

from gyver.utils import json

from .interface import AsyncCacheInterface
from .interface import CacheInterface

T = typing.TypeVar("T")


class AsyncCacheMap:
    def __init__(self, cache: AsyncCacheInterface, name: str) -> None:
        self._cache = cache
        self._name = name

    async def get(
        self, name: str, cast: typing.Callable[[typing.Any], T] = json.loads
    ) -> T:
        return await self._cache.map_get(self._name, name, cast)

    async def set(
        self,
        name: str,
        value: typing.Any,
        dumps: typing.Callable[[typing.Any], str] = json.dumps,
    ) -> None:
        return await self._cache.map_set(self._name, name, value, dumps)

    async def delete(self, name: str):
        return await self._cache.delete(name, self._name)


class CacheMap:
    def __init__(self, cache: CacheInterface, name: str) -> None:
        self._cache = cache
        self._name = name

    def get(self, name: str, cast: typing.Callable[[typing.Any], T] = json.loads) -> T:
        return self._cache.map_get(self._name, name, cast)

    def set(
        self,
        name: str,
        value: typing.Any,
        dumps: typing.Callable[[typing.Any], str] = json.dumps,
    ) -> None:
        return self._cache.map_set(self._name, name, value, dumps)

    def delete(self, name: str):
        return self._cache.delete(name, self._name)
