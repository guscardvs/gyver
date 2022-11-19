import re
import shlex
from typing import Callable
from typing import TypeVar

_to_camel_regexp = re.compile("_([a-zA-Z])")
_to_snake_regexp = re.compile("([a-z])([A-Z])")


def to_snake(camel_string: str) -> str:
    return _to_snake_regexp.sub(r"\1_\2", camel_string).lower()


def to_camel(snake_string: str) -> str:
    return _to_camel_regexp.sub(
        lambda match: match[1].upper(), snake_string
    ).removesuffix("_")


def upper_camel(snake_string: str):
    val = to_camel(snake_string)
    return val and val[0].upper() + val[1:]


T = TypeVar("T")

OuterCastT = TypeVar("OuterCastT", list, tuple, set)


def make_lex_separator(
    outer_cast: type[OuterCastT], cast: type = str
) -> Callable[[str], OuterCastT]:
    def wrapper(value: str) -> OuterCastT:
        lex = shlex.shlex(value, posix=True)
        lex.whitespace = ","
        lex.whitespace_split = True
        return outer_cast(cast(item.strip()) for item in lex)

    return wrapper


comma_separated = make_lex_separator(tuple, str)
