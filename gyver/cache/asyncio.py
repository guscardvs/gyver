from typing import Literal
from typing import Optional
from typing import overload

from gyver.utils import lazyfield

from .config import CacheConfig
from .interface import AsyncCacheInterface
from .mapper import AsyncCacheMap
from .mock import MockAsyncCache
from .redis import AsyncRedisWrapper


class AsyncCacheProvider:
    @overload
    def __init__(self, *, config: CacheConfig):
        ...

    @overload
    def __init__(self, *, test: Literal[True]):
        ...

    def __init__(
        self, *, config: Optional[CacheConfig] = None, test: bool = False
    ) -> None:
        self._config = config
        self._test = test

    @staticmethod
    def _make_concrete(
        config: Optional[CacheConfig], test: bool
    ) -> AsyncCacheInterface:
        return MockAsyncCache() if test else AsyncRedisWrapper(config)

    @lazyfield
    def interface(self):
        return self._make_concrete(self._config, self._test)

    def mapper(self, name: str) -> AsyncCacheMap:
        return AsyncCacheMap(self.interface, name)
