import typing
from datetime import datetime

from gyver.utils import json

T = typing.TypeVar("T")


class AsyncCacheInterface(typing.Protocol):
    async def get(
        self, name: str, cast: typing.Callable[[typing.Any], T] = json.loads
    ) -> T:
        ...

    async def set(
        self,
        name: str,
        value: typing.Any,
        expires_at: typing.Union[datetime, typing.Literal[-1]],
        dumps: typing.Callable[[typing.Any], str] = json.dumps,
    ) -> None:
        ...

    async def map_get(
        self,
        map_name: str,
        name: str,
        cast: typing.Callable[[typing.Any], T] = json.loads,
    ) -> T:
        ...

    async def map_set(
        self,
        map_name: str,
        name: str,
        value: typing.Any,
        dumps: typing.Callable[[typing.Any], str] = json.dumps,
    ) -> None:
        ...

    async def delete(self, name: str, map_name: typing.Optional[str] = None) -> None:
        ...


class CacheInterface(typing.Protocol):
    def get(self, name: str, cast: typing.Callable[[typing.Any], T] = json.loads) -> T:
        ...

    def set(
        self,
        name: str,
        value: typing.Any,
        expires_at: typing.Union[datetime, typing.Literal[-1]],
        dumps: typing.Callable[[typing.Any], str] = json.dumps,
    ) -> None:
        ...

    def map_get(
        self,
        map_name: str,
        name: str,
        cast: typing.Callable[[typing.Any], T] = json.loads,
    ) -> T:
        ...

    def map_set(
        self,
        map_name: str,
        name: str,
        value: typing.Any,
        dumps: typing.Callable[[typing.Any], str] = json.dumps,
    ) -> None:
        ...

    def delete(self, name: str, map_name: typing.Optional[str] = None) -> None:
        ...
