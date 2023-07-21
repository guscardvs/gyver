import re
import shlex
from typing import Callable
from typing import TypeVar

_to_camel_regexp = re.compile("_([a-zA-Z])")
_to_snake_regexp = re.compile("([a-z])([A-Z])")


def to_snake(camel_string: str) -> str:
    """
    The to_snake function converts camelCase strings to snake_case.

    :param camel_string: str: Pass the camelcase string to be converted
    :return: A string in snake_case
    """
    return _to_snake_regexp.sub(r"\1_\2", camel_string).lower()


def to_camel(snake_string: str) -> str:
    """
    The to_camel function converts a snake_string to camelCase.

    :param snake_string: str: Pass the string that is to be converted
    :return: A string that is converted from snake_case to camelcase
    """
    return _to_camel_regexp.sub(
        lambda match: match[1].upper(), snake_string
    ).removesuffix("_")


def to_pascal(snake_string: str):
    """
    The to_pascal function converts a snake_case string to an PascalCase string.

    :param snake_string: str: Pass in the string that we want to convert
    :return: A string that is the snake_string converted to camel
    case and with the first letter capitalized
    """
    val = to_camel(snake_string)
    return val and val[0].upper() + val[1:]


# Compat
upper_camel = to_pascal


def to_lower_kebab(camel_string: str) -> str:
    """
    The to_lower_kebab function converts camelCase strings to kebab-case.

    :param camel_string: str: Pass the camelCase string to be converted
    :return: A string in kebab-case
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

    :param outer_cast: The type to cast the resulting separated values into (e.g., list, tuple, set).
    :param cast: The type to which each individual item will be cast (default: str).
    :return: A callable that separates a string into an instance of outer_cast with casted items.

    Usage example:
    comma_separated = make_lex_separator(tuple, str)
    result = comma_separated("a, b, c")
    print(result)  # Output: ('a', 'b', 'c')
    """

    def wrapper(value: str) -> OuterCastT:
        lex = shlex.shlex(value, posix=True)
        lex.whitespace = ","
        lex.whitespace_split = True
        return outer_cast(cast(item.strip()) for item in lex)

    return wrapper


comma_separated = make_lex_separator(tuple, str)
