import functools
import typing

from typing_extensions import Self
from typing import Any

from gyver.exc import InvalidField

T = typing.TypeVar("T")
SelfT = typing.TypeVar("SelfT")

_obj_setattr = object.__setattr__
_obj_delattr = object.__delattr__
_obj_getattr = object.__getattribute__


class lazyfield(typing.Generic[SelfT, T]):
    """
    A descriptor class that can be used as a decorator for a method on a class.
    When the decorated method is accessed on an instance, it will check if the
    instance has an attribute with the same name as the method but with an
    underscore prefix. If the attribute does not exist, it will call the decorated
    method on the instance and set the result as the attribute's value.
    Subsequent accesses will return the cached value, avoiding unnecessary
    recalculation or computation.
    """

    def __init__(self, func: typing.Callable[[SelfT], T]) -> None:
        """
        func : callable
            The function that will be decorated. This function should take
            a single argument, which is the instance of the class it is a
            method of.
        """
        self._func = func

    def __set_name__(self, owner: type[SelfT], name: str):
        self.public_name = name
        self.private_name = f"_lazyfield_{name}"

    @typing.overload
    def __get__(self, instance: SelfT, owner: type[SelfT]) -> T:
        ...

    @typing.overload
    def __get__(
        self, instance: typing.Literal[None], owner: type[SelfT]
    ) -> Self:
        ...

    def __get__(
        self,
        instance: typing.Optional[SelfT],
        owner: typing.Optional[type[SelfT]] = None,
    ) -> typing.Union[T, Self]:
        if not instance:
            return self
        try:
            val = typing.cast(
                T,
                _obj_getattr(
                    instance,
                    self.private_name,
                ),
            )
        except AttributeError:
            val = self._try_set(instance)
        return val

    def _try_set(self, instance: SelfT) -> T:
        try:
            val = self._func(instance)
        except Exception as e:
            # remove exception context to create easier traceback
            raise e from None
        else:
            _obj_setattr(instance, self.private_name, val)
            return val

    def __set__(self, instance: SelfT, value: T):
        self.manual_set(instance, value)

    def __delete__(self, instance: SelfT):
        self.cleanup(instance)

    def cleanup(self, instance: SelfT):
        _obj_delattr(instance, self.private_name)

    def manual_set(self, instance: SelfT, value: T):
        _obj_setattr(instance, self.private_name, value)


class asynclazyfield(typing.Generic[SelfT, T]):
    def __init__(
        self,
        func: typing.Callable[
            [SelfT], typing.Coroutine[typing.Any, typing.Any, T]
        ],
    ) -> None:
        """
        func : callable
            The function that will be decorated. This function should take
            a single argument, which is the instance of the class it is a
            method of.
        """
        self._func = func

    def __set_name__(self, owner: type[SelfT], name: str):
        self.public_name = name
        self.private_name = f"_lazyfield_{name}"

    async def __call__(self, instance: SelfT) -> T:
        try:
            val = typing.cast(
                T,
                _obj_getattr(
                    instance,
                    self.private_name,
                ),
            )
        except AttributeError:
            val = await self._try_set(instance)
        return val

    async def _try_set(self, instance: SelfT) -> T:
        try:
            result = await self._func(instance)
        except Exception as e:
            raise e from None
        else:
            _obj_setattr(instance, self.private_name, result)
            return result

    @typing.overload
    def __get__(
        self, instance: SelfT, owner
    ) -> typing.Callable[[], typing.Coroutine[Any, Any, T]]:
        ...

    @typing.overload
    def __get__(self, instance: typing.Literal[None], owner) -> Self:
        ...

    def __get__(
        self, instance: typing.Optional[SelfT], owner=None
    ) -> typing.Union[
        typing.Callable[[], typing.Coroutine[Any, Any, T]], Self
    ]:
        if not instance:
            return self
        return functools.partial(self.__call__, instance=instance)


@functools.lru_cache(32)
def _getlazy(
    instance: Any, attribute: str
) -> typing.Union[lazyfield, asynclazyfield]:
    lazy = getattr(type(instance), attribute, None)
    if not isinstance(lazy, (lazyfield, asynclazyfield)):
        raise InvalidField(
            f"Field {attribute} expected to be lazy but received {type(lazy)}"
        )
    return lazy


def setlazy(
    instance: Any, attribute: str, value: Any, bypass_setattr: bool = False
):
    lazy = _getlazy(instance, attribute)
    setter = _obj_setattr if bypass_setattr else setattr
    setter(instance, lazy.private_name, value)


def dellazy(instance: Any, attribute: str, bypass_delattr: bool = False):
    lazy = _getlazy(instance, attribute)
    deleter = _obj_delattr if bypass_delattr else delattr
    deleter(instance, lazy.private_name)
