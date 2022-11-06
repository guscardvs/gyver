from typing import TypeVar

T = TypeVar("T", bound=Exception)


def panic(exc: type[T], message: str) -> T:
    return exc(message.removesuffix("!") + "!")
