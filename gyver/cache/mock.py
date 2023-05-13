import asyncio
import typing
from contextlib import asynccontextmanager
from contextlib import contextmanager
from contextlib import suppress
from datetime import datetime
from datetime import timezone
from queue import Queue

from gyver.attrs import define
from gyver.attrs import info

from gyver.exc import CacheMiss
from gyver.utils import json
from gyver.utils import lazyfield

from .interface import AsyncCacheInterface
from .interface import CacheInterface

T = typing.TypeVar("T")


@define
class MockAsyncCache(AsyncCacheInterface):
    key_map: typing.MutableMapping[str, typing.Any] = info(default_factory=dict)

    @lazyfield
    def _queue(self) -> asyncio.Queue[object]:
        size = 10
        queue = asyncio.Queue(size)
        for _ in range(size):
            queue.put_nowait(object())
        return queue

    @asynccontextmanager
    async def _in_queue(self):
        try:
            await self._queue.get()
            yield
        finally:
            await self._queue.put(object())

    async def get(
        self, name: str, cast: typing.Callable[[typing.Any], T] = json.loads
    ) -> T:
        async with self._in_queue():
            try:
                response, exp = self.key_map[name]
            except KeyError:
                raise CacheMiss from None
            else:
                if exp is not None and exp <= datetime.now(timezone.utc):
                    raise CacheMiss
                return cast(response)

    async def set(
        self,
        name: str,
        value: typing.Any,
        expires_at: typing.Union[datetime, typing.Literal[-1]],
        dumps: typing.Callable[[typing.Any], str] = json.dumps,
    ) -> None:
        async with self._in_queue():
            self.key_map[name] = (
                dumps(value),
                expires_at if expires_at != -1 else None,
            )

    async def map_get(
        self,
        map_name: str,
        name: str,
        cast: typing.Callable[[typing.Any], T] = json.loads,
    ) -> T:
        async with self._in_queue():
            try:
                val = self.key_map[map_name][name]
            except KeyError:
                raise CacheMiss from None
            else:
                return cast(val)

    async def map_set(
        self,
        map_name: str,
        name: str,
        value: typing.Any,
        dumps: typing.Callable[[typing.Any], str] = json.dumps,
    ) -> None:
        async with self._in_queue():
            if map_name not in self.key_map:
                self.key_map[map_name] = {}
            self.key_map[map_name][name] = dumps(value)

    async def delete(self, name: str, map_name: typing.Optional[str] = None) -> None:
        async with self._in_queue():
            used_map = self.key_map
            if map_name is not None:
                if map_name not in self.key_map:
                    return
                used_map = self.key_map[map_name]

            with suppress(KeyError):
                del used_map[name]


_KeyMapType = typing.MutableMapping[
    str,
    typing.Union[
        tuple[typing.Any, typing.Optional[datetime]],
        dict[str, typing.Any],
    ],
]


@define
class MockCache(CacheInterface):
    key_map: _KeyMapType = info(default_factory=info)

    @lazyfield
    def _queue(self) -> Queue[object]:
        size = 10
        queue = Queue(size)
        for _ in range(size):
            queue.put_nowait(object())
        return queue

    @contextmanager
    def _in_queue(self):
        try:
            self._queue.get()
            yield
        finally:
            self._queue.put(object())

    def get(self, name: str, cast: typing.Callable[[typing.Any], T] = json.loads) -> T:
        with self._in_queue():
            try:
                val = self.key_map[name]
                if isinstance(val, dict):
                    raise CacheMiss
                response, exp = val
            except KeyError:
                raise CacheMiss from None
            else:
                if exp is not None and exp <= datetime.now(timezone.utc):
                    raise CacheMiss
                return cast(response)

    def set(
        self,
        name: str,
        value: typing.Any,
        expires_at: typing.Union[datetime, typing.Literal[-1]],
        dumps: typing.Callable[[typing.Any], str] = json.dumps,
    ) -> None:
        with self._in_queue():
            self.key_map[name] = (
                dumps(value),
                expires_at if expires_at != -1 else None,
            )

    def map_get(
        self,
        map_name: str,
        name: str,
        cast: typing.Callable[[typing.Any], T] = json.loads,
    ) -> T:
        with self._in_queue():
            try:
                mapping = self.key_map[map_name]
                if not isinstance(mapping, dict):
                    raise CacheMiss
                val = mapping[name]
            except KeyError:
                raise CacheMiss from None
            else:
                return cast(val)

    def map_set(
        self,
        map_name: str,
        name: str,
        value: typing.Any,
        dumps: typing.Callable[[typing.Any], str] = json.dumps,
    ) -> None:
        with self._in_queue():
            if map_name not in self.key_map:
                self.key_map[map_name] = {}

            if isinstance(self.key_map[map_name], tuple):
                self.key_map[map_name] = {}
            mapping = typing.cast(dict, self.key_map[map_name])
            mapping[name] = dumps(value)

    def delete(self, name: str, map_name: typing.Optional[str] = None) -> None:
        with self._in_queue():
            used_map = self.key_map
            if map_name is not None:
                if map_name not in self.key_map:
                    return
                used_map = self.key_map[map_name]
                if isinstance(used_map, tuple):
                    return

            with suppress(KeyError):
                used_map.pop(name, None)
