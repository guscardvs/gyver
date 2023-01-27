import re
from typing import Callable
from typing import TypeVar
from typing import Union

from typing_extensions import Concatenate
from typing_extensions import ParamSpec

T = TypeVar("T")
R = TypeVar("R")
P = ParamSpec("P")


def try_cast(
    val: T, cast: Callable[Concatenate[T, P], R], *args: P.args, **kwargs: P.kwargs
) -> Union[T, R]:
    try:
        return cast(val, *args, **kwargs)
    except Exception:
        return val


def utf8(val: str):
    return try_cast(val, str.encode, "utf-8")


PERCENT_REGEX = r"\%[a-fA-F\d][a-fA-F\d]"


is_valid_encoded_path = re.compile(
    r"^([\w%s]|(%s))*$" % (re.escape("-.~:@!$&'()*+,;="), PERCENT_REGEX)
)
