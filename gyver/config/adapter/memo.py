from typing import Any, TypeVar

from config.interface import ConfigLike
from lazyfields import lazyfield

from gyver.attrs import define, private

from .factory import DEFAULT_CONFIG, AdapterConfigFactory

T = TypeVar("T")


@define
class MemoFactory:
    config: ConfigLike = DEFAULT_CONFIG
    _memo_map: dict[tuple[str, type], Any] = private(initial_factory=dict)
    _primary: dict[type, Any] = private(initial_factory=dict)

    @lazyfield
    def _internal(self) -> AdapterConfigFactory:
        return AdapterConfigFactory(self.config)

    def load(
        self,
        model_cls: type[T],
        __prefix__: str = "",
        __sep__: str = "__",
        __primary__: bool = False,
        *,
        presets: dict[str, Any] | None = None,
        **defaults: Any,
    ) -> T:
        if memo := self._memo_map.get((__prefix__, model_cls)):
            return memo
        if (memo := self._primary.get(model_cls)) and not __prefix__:
            return memo
        memo = self._internal.load(
            model_cls,
            __prefix__,
            __sep__,
            presets=presets,
            **defaults,
        )
        self._memo_map[(__prefix__, model_cls)] = memo
        if __primary__:
            self._primary[model_cls] = memo
        return memo
