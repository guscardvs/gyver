import re
import shlex
from typing import Callable
from typing import TypeVar

from gyver.utils.helpers import deprecated

_to_camel_regexp = re.compile("_([a-zA-Z])")
_to_snake_regexp = re.compile("([a-z])([A-Z])")


def to_snake(camel_string: str) -> str:
    """
    Convert a camelCase string to snake_case.

    Args:
        camel_string (str): The camelCase string to be converted.

    Returns:
        str: The converted string in snake_case.
    """
    return _to_snake_regexp.sub(r"\1_\2", camel_string).lower()


def to_camel(snake_string: str) -> str:
    """
    Convert a snake_case string to camelCase.

    Args:
        snake_string (str): The snake_case string to be converted.

    Returns:
        str: The converted string in camelCase.
    """
    return _to_camel_regexp.sub(
        lambda match: match[1].upper(), snake_string
    ).removesuffix("_")


def to_pascal(snake_string: str) -> str:
    """
    Convert a snake_case string to PascalCase.

    Args:
        snake_string (str): The snake_case string to be converted.

    Returns:
        str: The converted string in PascalCase.
    """
    val = to_camel(snake_string)
    return val and val[0].upper() + val[1:]


# Compat
@deprecated
def upper_camel(snake_string: str):
    """
    Deprecated:
        Use [to_pascal][gyver.utils.strings.to_pascal] instead.
    """
    return to_pascal(snake_string)


def to_lower_kebab(camel_string: str) -> str:
    """
    Convert camelCase strings to kebab-case.

    Args:
        camel_string (str): The camelCase string to be converted.

    Returns:
        str: The converted string in kebab-case.
    """
    snake_string = to_snake(camel_string)
    return snake_string.replace("_", "-")


T = TypeVar("T")

OuterCastT = TypeVar("OuterCastT", list, tuple, set)


def make_lex_separator(
    outer_cast: type[OuterCastT], cast: type = str
) -> Callable[[str], OuterCastT]:
    """
    Create a lexer-based separator function.

    Args:
        outer_cast (type): The type to cast the resulting separated values into.
        cast (type): The type to which each individual item will be cast (default: str).

    Returns:
        Callable[[str], OuterCastT]: A callable that separates a string into an instance of outer_cast with casted items.

    Examples:
    
        >>> comma_separated = make_lex_separator(tuple, str)
        >>> result = comma_separated("a, b, c")
        >>> print(result)
        ('a', 'b', 'c')
    """

    def wrapper(value: str) -> OuterCastT:
        lex = shlex.shlex(value, posix=True)
        lex.whitespace = ","
        lex.whitespace_split = True
        return outer_cast(cast(item.strip()) for item in lex)

    return wrapper


comma_separated = make_lex_separator(tuple, str)
