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
        """
        Generates the name of the private attribute based on the provided public name.

        Args:
            public_name (str): The public name of the lazy-loaded property.

        Returns:
            str: The generated private attribute name."""
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
        Initializes the lazy field descriptor.

        Args:
            func (callable): The function that will be decorated."""
        self._func = func

    def __set_name__(self, owner: type[SelfT], name: str):
        """
        Sets the public and private names for the lazy field descriptor.

        Args:
            owner (type): The class that owns the descriptor.
            name (str): The name of the attribute."""
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
            result = self._func(instance)
        except Exception as e:
            # remove exception context to create easier traceback
            raise e from None
        else:
            force_set(instance, self.public_name, result)
            return result

    def __set__(self, instance: SelfT, value: T):
        setlazy(instance, self.public_name, value)

    def __delete__(self, instance: SelfT):
        dellazy(instance, self.public_name)


class asynclazyfield(lazy, typing.Generic[SelfT, T]):
    """
    A descriptor class for asynchronously lazy-loading attributes on a class.

    When the decorated method is accessed on an instance, it will check if the
    instance has an attribute with the same name as the method but with an
    underscore prefix. If the attribute does not exist, it will call the decorated
    asynchronous method on the instance and set the result as the attribute's value.
    Subsequent accesses will return the cached value, avoiding unnecessary
    recalculation or computation.
    """

    def __init__(
        self,
        func: typing.Callable[
            [SelfT], typing.Coroutine[typing.Any, typing.Any, T]
        ],
    ) -> None:
        """
        Initializes the asynclazyfield descriptor.

        Args:
            func (callable): The asynchronous function that will be decorated."""
        self._func = func

    def __set_name__(self, owner: type[SelfT], name: str):
        """
        Set the public and private names for the asynclazyfield descriptor.

        Args:
            owner (type): The class that owns the descriptor.
            name (str): The name of the attribute.
        """
        self.public_name = name
        self.private_name = self._make_private(name)

    async def __call__(self, instance: SelfT) -> T:
        """
        Call the asynchronous method to load the attribute's value.

        Args:
            instance (SelfT): The instance of the class.

        Returns:
            T: The loaded value of the attribute.
        """
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
        """
        Attempt to set the value of the attribute using the asynchronous method.

        Args:
            instance (SelfT): The instance of the class.

        Returns:
            T: The loaded value of the attribute.

        Raises:
            Exception: If the asynchronous method raises an exception.
        """
        try:
            result = await self._func(instance)
        except Exception as e:
            raise e from None
        else:
            force_set(instance, self.public_name, result)
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
        """
        Get the wrapped asynchronous method or the descriptor itself.

        Args:
            instance (typing.Optional[SelfT]): The instance of the class.
            owner (type[SelfT]): The class that owns the descriptor.

        Returns:
            Union[
                typing.Callable[[], typing.Coroutine[Any, Any, T]],
                Self
            ]: The asynchronous method or the descriptor itself.
        """
        if not instance:
            return self
        return functools.partial(self.__call__, instance=instance)


def _getlazy(instance: Any, attribute: str) -> lazy:
    """
    Get the lazy descriptor associated with the specified attribute on an instance.

    Args:
        instance (Any): The instance to retrieve the descriptor from.
        attribute (str): The name of the lazy-loaded property.

    Returns:
        lazy: The lazy descriptor associated with the attribute.

    Raises:
        InvalidField: If the attribute is not a lazy descriptor.
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
    """
    Set the value of a lazy-loaded property on an instance.

    Args:
        instance (Any): The instance to set the property on.
        attribute (str): The name of the lazy-loaded property.
        value (Any): The value to set for the property.
        bypass_setattr (bool): If True, directly set the attribute using `object.__setattr__`
                               to bypass immutability issues. (default: False)

    Raises:
        InvalidField: If the attribute is not a lazy descriptor.
    """
    lazy = _getlazy(instance, attribute)
    setter = _obj_setattr if bypass_setattr else setattr
    setter(instance, lazy.private_name, value)


def force_set(instance: Any, attribute: str, value: Any):
    """
    Forcefully set the value of a lazy-loaded property on an instance.

    Args:
        instance (Any): The instance to set the property on.
        attribute (str): The name of the lazy-loaded property.
        value (Any): The value to set for the property.
    """
    setlazy(instance, attribute, value, bypass_setattr=True)


def dellazy(instance: Any, attribute: str, bypass_delattr: bool = False):
    """
    Delete the value of a lazy-loaded property on an instance.

    Args:
        instance (Any): The instance to delete the property from.
        attribute (str): The name of the lazy-loaded property.
        bypass_delattr (bool): If True, directly delete the attribute using `object.__delattr__`
                               to bypass immutability issues. (default: False)

    Raises:
        InvalidField: If the attribute is not a lazy descriptor.
    """
    lazy = _getlazy(instance, attribute)
    deleter = _obj_delattr if bypass_delattr else delattr
    deleter(instance, lazy.private_name)


def force_del(instance: Any, attribute: str):
    """
    Forcefully delete the value of a lazy-loaded property on an instance.

    Args:
        instance (Any): The instance to set the property on.
        attribute (str): The name of the lazy-loaded property.
    """
    dellazy(instance, attribute, bypass_delattr=True)


SENTINEL = object()


def is_initialized(instance: Any, attribute: str) -> bool:
    lazyf = _getlazy(instance, attribute)
    return getattr(instance, lazyf.private_name, SENTINEL) is not SENTINEL
