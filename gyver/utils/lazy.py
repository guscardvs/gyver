import functools
import typing
from typing import Any

from typing_extensions import Self

from gyver.exc import InvalidField

T = typing.TypeVar("T")
SelfT = typing.TypeVar("SelfT")

_obj_setattr = object.__setattr__
_obj_delattr = object.__delattr__
_obj_getattr = object.__getattribute__


class lazy:
    """Represents a lazy descriptor"""

    private_name: str
    public_name: str

    @staticmethod
    def _make_private(public_name: str) -> str:
        """Generate the name of the private attribute based on the provided public name.
        :param public_name: The public name of the lazy-loaded property.
        :return: The generated private attribute name.
        """
        return f"_lazyfield_{public_name}"


class lazyfield(lazy, typing.Generic[SelfT, T]):
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
        self.private_name = self._make_private(name)

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
        del owner
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
            force_set(instance, self.public_name, val)
            return val

    def __set__(self, instance: SelfT, value: T):
        setlazy(instance, self.public_name, value)

    def __delete__(self, instance: SelfT):
        dellazy(instance, self.public_name)


class asynclazyfield(lazy, typing.Generic[SelfT, T]):
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
        self.private_name = self._make_private(name)

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


def _getlazy(instance: Any, attribute: str) -> lazy:
    """Get the lazy descriptor associated with the specified attribute on an instance.

    :param instance: The instance to retrieve the descriptor from.
    :param attribute: The name of the lazy-loaded property.
    :return: The lazy descriptor associated with the attribute.
    :raises InvalidField: If the attribute is not a lazy descriptor.
    """
    lazyf = getattr(type(instance), attribute, None)
    if not isinstance(lazyf, lazy):
        raise InvalidField(
            f"Field {attribute} expected to be lazy but received {type(lazyf)}"
        )
    return lazyf


def setlazy(
    instance: Any, attribute: str, value: Any, bypass_setattr: bool = False
):
    """Set the value of a lazy-loaded property on an instance.

    :param instance: The instance to set the property on.
    :param attribute: The name of the lazy-loaded property.
    :param value: The value to set for the property.
    :param bypass_setattr: If True, directly set the attribute using `object.__setattr__`
                           to bypass immutability issues. (default: False)
    :raises InvalidField: If the attribute is not a lazy descriptor.
    """
    lazy = _getlazy(instance, attribute)
    setter = _obj_setattr if bypass_setattr else setattr
    setter(instance, lazy.private_name, value)


def force_set(instance: Any, attribute: str, value: Any):
    setlazy(instance, attribute, value, bypass_setattr=True)


def dellazy(instance: Any, attribute: str, bypass_delattr: bool = False):
    """Delete the value of a lazy-loaded property on an instance.

    :param instance: The instance to delete the property from.
    :param attribute: The name of the lazy-loaded property.
    :param bypass_delattr: If True, directly delete the attribute using `object.__delattr__`
                           to bypass immutability issues. (default: False)
    :raises InvalidField: If the attribute is not a lazy descriptor.
    """
    lazy = _getlazy(instance, attribute)
    deleter = _obj_delattr if bypass_delattr else delattr
    deleter(instance, lazy.private_name)


def force_del(instance: Any, attribute: str):
    dellazy(instance, attribute, bypass_delattr=True)
