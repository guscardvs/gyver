from typing import Literal
from typing import Optional
from typing import overload

from gyver.attrs import call_init
from gyver.attrs import define

from gyver.utils import lazyfield

from .config import CacheConfig
from .interface import CacheInterface
from .mapper import CacheMap
from .mock import MockCache
from .redis import RedisWrapper


@define
class CacheProvider:
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
    def _make_concrete(config: Optional[CacheConfig], test: bool) -> CacheInterface:
        if test:
            return MockCache()
        return RedisWrapper() if config is None else RedisWrapper(config)

    @lazyfield
    def interface(self):
        return self._make_concrete(self.config, self.test)

    def mapper(self, name: str) -> CacheMap:
        return CacheMap(self.interface, name)
