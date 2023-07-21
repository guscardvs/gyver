from typing import Any
from typing import Callable
from typing import Protocol
from typing import TypeVar
from typing import Union
from typing import overload


class MISSING:
    pass


def _default_cast(a: Any):
    return a


T = TypeVar("T")


class ConfigLike(Protocol):
    def get(
        self,
        name: str,
        cast: Callable = _default_cast,
        default: Union[Any, type[MISSING]] = MISSING,
    ) -> Any:
        ...

    @overload
    def __call__(
        self,
        name: str,
        cast: Union[Callable[[Any], T], type[T]] = _default_cast,
        default: type[MISSING] = MISSING,
    ) -> T:
        ...

    @overload
    def __call__(
        self,
        name: str,
        cast: Union[Callable[[Any], T], type[T]] = _default_cast,
        default: T = ...,
    ) -> T:
        ...

    def __call__(
        self,
        name: str,
        cast: Union[Callable[[Any], T], type[T]] = _default_cast,
        default: Union[T, type[MISSING]] = MISSING,
    ) -> T:
        ...
