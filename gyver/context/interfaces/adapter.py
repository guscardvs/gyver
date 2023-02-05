import typing

from gyver.context.typedef import T


class Adapter(typing.Protocol[T]):
    def is_closed(self, client: T) -> bool:
        """Returns if client state is closed or released"""
        ...

    def release(self, client: T) -> None:
        """Closes or releases client"""
        ...

    def new(self) -> T:
        """Creates new client"""
        ...


class AsyncAdapter(typing.Protocol[T]):
    """Represents an Adapter to a Specific Service"""

    async def is_closed(self, client: T) -> bool:
        """Returns if client state is closed or released"""
        ...

    async def release(self, client: T) -> None:
        """Closes or releases client"""
        ...

    async def new(self) -> T:
        """Creates new client"""
        ...


class AtomicAdapter(Adapter[T], typing.Protocol[T]):
    """Represents an Adapter to a Specific Service that
    can do atomic operations"""

    def begin(self, client: T) -> None:
        ...

    def commit(self, client: T) -> None:
        ...

    def rollback(self, client: T) -> None:
        ...

    def in_atomic(self, client: T) -> bool:
        ...


class AtomicAsyncAdapter(AsyncAdapter[T], typing.Protocol[T]):
    """Represents an Adapter to a Specific Service that
    can do atomic operations"""

    async def begin(self, client: T) -> None:
        ...

    async def commit(self, client: T) -> None:
        ...

    async def rollback(self, client: T) -> None:
        ...

    async def in_atomic(self, client: T) -> bool:
        ...
