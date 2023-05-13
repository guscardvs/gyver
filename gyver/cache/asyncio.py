from typing import Literal
from typing import Optional
from typing import overload

from gyver.attrs import call_init
from gyver.attrs import define

from gyver.utils import lazyfield

from .config import CacheConfig
from .interface import AsyncCacheInterface
from .mapper import AsyncCacheMap
from .mock import MockAsyncCache
from .redis import AsyncRedisWrapper


@define
class AsyncCacheProvider:
    config: CacheConfig
    test: bool

    @overload
    def __init__(self, *, config: CacheConfig):
        ...

    @overload
    def __init__(self, *, test: Literal[True]):
        ...

    def __init__(
        self, *, config: Optional[CacheConfig] = None, test: bool = False
    ) -> None:
        call_init(self, config, test)

    @staticmethod
    def _make_concrete(
        config: Optional[CacheConfig], test: bool
    ) -> AsyncCacheInterface:
        if test:
            return MockAsyncCache()
        return AsyncRedisWrapper(config) if config is not None else AsyncRedisWrapper()

    @lazyfield
    def interface(self):
        return self._make_concrete(self.config, self.test)

    def mapper(self, name: str) -> AsyncCacheMap:
        return AsyncCacheMap(self.interface, name)
