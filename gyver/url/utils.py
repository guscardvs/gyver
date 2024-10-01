import re
from collections.abc import Callable
from typing import Concatenate, TypeVar

from typing_extensions import ParamSpec

T = TypeVar("T")
R = TypeVar("R")
P = ParamSpec("P")


def try_cast(
    val: T, cast: Callable[Concatenate[T, P], R], *args: P.args, **kwargs: P.kwargs
) -> T | R:
    """
    Try to cast a value to a different type using a provided casting function.

    :param val: The value to be cast.
    :param cast: The casting function.
    :param args: Positional arguments to be passed to the casting function.
    :param kwargs: Keyword arguments to be passed to the casting function.
    :return: The casted value if successful, otherwise the original value.
    """
    try:
        return cast(val, *args, **kwargs)
    except Exception:
        return val


def utf8(val: str):
    """
    Encode a string using UTF-8.

    :param val: The string to be encoded.
    :return: The encoded string.
    """
    return try_cast(val, str.encode, "utf-8")


PERCENT_REGEX = r"\%[a-fA-F\d][a-fA-F\d]"


is_valid_encoded_path = re.compile(
    r"^([\w{}]|({}))*$".format(re.escape("-.~:@!$&'()*+,;="), PERCENT_REGEX)
)
