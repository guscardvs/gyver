import functools
import warnings
from collections.abc import Callable
from typing import TYPE_CHECKING, ParamSpec, TypeVar

from gyver.misc import functions, json, merge_dicts, strings, timezone
from gyver.misc.exc import scream

T = TypeVar("T")
P = ParamSpec("P")
ExcT = TypeVar("ExcT", bound=Exception)

to_snake = strings.to_snake
to_pascal = strings.to_pascal
to_camel = strings.to_camel
upper_camel = strings.upper_camel
cache = functions.cache


def panic(exc: type[ExcT], message: str, *args) -> ExcT:
    """
    Create an instance of the specified exception class with a modified error message.

    This function creates an exception instance by calling the constructor of the
    specified exception class with the modified error message and any additional
    arguments provided.

    Args:
        exc (type[T]): The exception class to instantiate.
        message (str): The error message for the exception.
        *args (Any): Additional arguments to pass to the exception constructor.

    Returns:
        T: An instance of the specified exception class.

    Examples:
        >>> class CustomError(Exception):
        ...     pass
        ...
        >>> error = panic(CustomError, "Something went wrong", "additional_info")
        >>> isinstance(error, CustomError)
        True
        >>> str(error)
        'Something went wrong! additional_info'
    """
    return scream(exc, message, *args)


def deprecated(func: Callable[P, T]) -> Callable[P, T]:
    """
    Mark a function as deprecated and issue a warning when it's used.

    Args:
        func (Callable[P, T]): The function to be marked as deprecated.

    Returns:
        Callable[P, T]: A wrapped version of the function that issues a warning on use.
    """

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


if TYPE_CHECKING:
    import typing_extensions as te

    deprecated = te.deprecated  # type: ignore


class DeprecatedClass:
    """
    A class to mark as deprecated.

    This class issues a deprecation warning when instantiated.
    """

    __warn_deprecated__ = False

    def __init__(self) -> None:
        if not type(self).__warn_deprecated__:
            warnings.warn(
                f"{'.'.join((type(self).__module__, type(self).__name__))} is "
                "deprecated and can be removed without notice",
                DeprecationWarning,
            )
            type(self).__warn_deprecated__ = True


__all__ = [
    "json",
    "merge_dicts",
    "timezone",
    "strings",
    "functions",
    "panic",
    "to_snake",
    "to_pascal",
    "to_camel",
    "upper_camel",
    "cache",
    "deprecated",
    "DeprecatedClass",
]
