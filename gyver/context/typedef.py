import typing

T = typing.TypeVar("T", bound=typing.ContextManager)
AsyncT = typing.TypeVar("AsyncT", bound=typing.AsyncContextManager)
