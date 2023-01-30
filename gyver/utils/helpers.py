import functools
import warnings
from typing import Callable
from typing import TypeVar
from typing import cast

from typing_extensions import ParamSpec

from .exc import panic


def _not_implemented(msg: str):
    def inner(*_, **__kwds__):
        raise panic(NotImplementedError, msg)

    return inner


P = ParamSpec("P")
T = TypeVar("T")


def frozen(cls: type[T]) -> type[T]:
    """Removes setattr and delattr from class"""
    type.__setattr__(
        cls,
        "__setattr__",
        _not_implemented(f"{cls.__name__} is frozen, cannot change values"),
    )
    type.__setattr__(
        cls,
        "__delattr__",
        _not_implemented(f"{cls.__name__} is frozen, cannot delete values"),
    )

    return cls


def cache(f: Callable[P, T]) -> Callable[P, T]:
    return cast(Callable[P, T], functools.cache(f))


def deprecated(func: Callable[P, T]) -> Callable[P, T]:
    @functools.wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        if not hasattr(func, "__warn_deprecated__"):
            warnings.warn(
                f"{func.__qualname__} is "
                "deprecated and can be removed without notice",
                DeprecationWarning,
            )
            func.__warn_deprecated__ = True
        return func(*args, **kwargs)

    return inner
