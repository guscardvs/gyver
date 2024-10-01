import inspect
import warnings
from collections.abc import Callable
from functools import WRAPPER_UPDATES, update_wrapper
from inspect import signature
from typing import Any, Literal, TypeVar
from collections.abc import Coroutine

from config import MISSING
from config.interface import ConfigLike
from lazyfields import asynclazyfield, lazyfield
from typing_extensions import ParamSpec
from typing import Concatenate

from gyver.attrs import call_init, define

from .factory import _DEFAULT_CONFIG, AdapterConfigFactory
from .mark import is_config

T = TypeVar("T")
SelfT = TypeVar("SelfT")
P = ParamSpec("P")


def load(
    cls: type[T],
    __prefix__: str = "",
    __sep__: str = "__",
    __kwargs_type__: Literal["presets", "defaults"] = "defaults",
    __config__: ConfigLike = _DEFAULT_CONFIG,
    **kwargs: Any,
) -> T:
    """
    Load configuration for a given class.

    Args:
        cls (type): The class to load configuration for.
        __prefix__ (str, optional): Prefix to prepend to configuration keys. Defaults to "".
        __sep__ (str, optional): Separator used between prefix and configuration keys. Defaults to "__".
        __kwargs_type__ (Literal["presets", "defaults"], optional):
            Type of configuration to load, either "presets" or "defaults". Defaults to "defaults".
        __config__ (ConfigLike, optional): Configuration backend to use. Defaults to _DEFAULT_CONFIG.
        **kwargs (Any): Additional keyword arguments.

    Returns:
        T: An instance of the class with configuration loaded.

    Raises:
        (Any): Raises exceptions related to loading and casting configuration values.
    """
    factory = AdapterConfigFactory(__config__)
    defaults = kwargs if __kwargs_type__ == "defaults" else {}
    return factory.load(
        cls,
        __prefix__=__prefix__,
        __sep__=__sep__,
        __kwargs_type__=__kwargs_type__,
        presets=kwargs if __kwargs_type__ == "presets" else None,
        **defaults,
    )


def parametrize(
    call: Callable[..., T],
    __prefix__: str = "",
    __sep__: str = "__",
    __kwargs_type__: Literal["presets", "defaults"] = "defaults",
    __config__: ConfigLike = _DEFAULT_CONFIG,
    __transform__: Callable[[str], str] = str.upper,
    **kwargs: Any,
) -> T:
    """
    Parameterize a callable function with configuration values.
    It is recommended to store the result of this function in a constant to avoid recomputation.

    Args:
        call (Callable): The callable function to parameterize.
        __prefix__ (str, optional): Prefix to prepend to parameter names. Defaults to "".
        __sep__ (str, optional): Separator used between prefix and parameter names. Defaults to "__".
        __kwargs_type__ (Literal["presets", "defaults"], optional):
            Type of configuration to load, either "presets" or "defaults". Defaults to "defaults".
        __config__ (ConfigLike, optional): Configuration backend to use. Defaults to _DEFAULT_CONFIG.
        __transform__ ((str) -> str): A callable that transforms the parameter names when searching the environment for configuration values.
            The default transformation is set to `str.upper`, converting names to uppercase.
        **kwargs (Any): Additional keyword arguments.

    Returns:
        T: The result of the callable function with parameterized values.

    Raises:
        (Any): Raises exceptions related to loading and casting configuration values.
    """
    sig = signature(call)
    prefix = (
        f"{__prefix__}_" if __prefix__ and not __prefix__.endswith("_") else __prefix__
    )
    args = {
        key: (
            __transform__(f"{prefix}{key}"),
            str if value.annotation is inspect._empty else value.annotation,
        )
        for key, value in sig.parameters.items()
        if not (key in kwargs and __kwargs_type__ == "presets")
    }
    defaults = (
        {__transform__(key): value for key, value in kwargs.items()} | kwargs
        if __kwargs_type__ == "defaults"
        else {}
    )
    presets = kwargs if __kwargs_type__ == "presets" else {}
    if not args:
        warnings.warn(f"No args could be inspected in function: {call.__name__}")
    vals = {
        key: __config__(prefix, _cast, defaults.get(key, MISSING))
        if not is_config(_cast)
        else load(
            _cast,
            __prefix__=prefix,
            __sep__=__sep__,
            __config__=__config__,
            __kwargs_type__=__kwargs_type__,
            **{key: value for key, value in defaults.items() if key.startswith(prefix)},
        )
        for key, (prefix, _cast) in args.items()
    } | presets
    return call(**vals)


@define
class AttributeLoader:
    __prefix__: str = ""
    __sep__: str = "__"
    __config__: ConfigLike = _DEFAULT_CONFIG
    __self_name__: str = "self"
    __transform__: Callable[[str], str] = str.upper

    def __init__(
        self,
        __prefix__: str = "",
        __sep__: str = "__",
        __config__: ConfigLike = _DEFAULT_CONFIG,
        __self_name__: str = "self",
        __transform__: Callable[[str], str] = str.upper,
    ) -> None:
        call_init(self, __prefix__, __sep__, __config__, __self_name__, __transform__)

    def lazy(self, method: Callable[Concatenate[SelfT, P], T]) -> lazyfield[SelfT, T]:
        def _parametrize(__self__: SelfT) -> T:
            return parametrize(
                method,
                __prefix__=self.__prefix__,
                __sep__=self.__sep__,
                __config__=self.__config__,
                __kwargs_type__="presets",
                __transform__=self.__transform__,
                **{self.__self_name__: __self__},
            )

        update_wrapper(
            _parametrize,
            method,
            ("__module__", "__name__", "__qualname__", "__doc__"),
            updated=WRAPPER_UPDATES,
        )
        return lazyfield(_parametrize)

    def asynclazy(
        self, method: Callable[Concatenate[SelfT, P], Coroutine[Any, Any, T]]
    ) -> asynclazyfield[SelfT, T]:
        def _parametrize(__self__: SelfT) -> Coroutine[Any, Any, T]:
            return parametrize(
                method,
                __prefix__=self.__prefix__,
                __sep__=self.__sep__,
                __config__=self.__config__,
                __kwargs_type__="presets",
                __transform__=self.__transform__,
                **{self.__self_name__: __self__},
            )

        update_wrapper(
            _parametrize,
            method,
            ("__module__", "__name__", "__qualname__", "__doc__"),
            updated=WRAPPER_UPDATES,
        )
        return asynclazyfield(_parametrize)


attribute = AttributeLoader()
