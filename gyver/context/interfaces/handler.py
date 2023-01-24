import typing

from gyver.context.typedef import AsyncT
from gyver.context.typedef import T
from gyver.utils import lazyfield

from .adapter import Adapter
from .adapter import AsyncAdapter


class Handler(typing.Protocol[T]):
    def __init__(self, adapter: Adapter[T]) -> None:
        ...

    def is_active(self) -> bool:
        """Returns if current handler has an active context"""
        ...

    @lazyfield
    def client(self) -> T:
        ...

    adapter: Adapter[T]

    def open(self) -> typing.ContextManager[None]:
        """Initializes an internal client"""
        ...

    def begin(self) -> typing.ContextManager[T]:
        """Returns initialized internal client
        or new client if none is found"""
        ...


class AsyncHandler(typing.Protocol[AsyncT]):
    def __init__(self, adapter: AsyncAdapter[AsyncT]) -> None:
        ...

    adapter: AsyncAdapter[AsyncT]

    def is_active(self) -> bool:
        """Returns if current handler has an active context"""
        ...

    async def client(self) -> AsyncT:
        """Returns internal client or creates a new one"""
        ...

    def open(self) -> typing.AsyncContextManager[None]:
        """Initializes an internal client"""
        ...

    def begin(self) -> typing.AsyncContextManager[AsyncT]:
        """Returns initialized internal client
        or new client if none is found"""
        ...
