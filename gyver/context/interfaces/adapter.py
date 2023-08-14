import typing

from gyver.context.typedef import T


class Adapter(typing.Protocol[T]):
    def is_closed(self, client: T) -> bool:
        """Returns whether the client state is closed or released."""
        ...

    def release(self, client: T) -> None:
        """Closes or releases the client."""
        ...

    def new(self) -> T:
        """Creates a new client."""
        ...


class AsyncAdapter(typing.Protocol[T]):
    """Represents an Adapter to a Specific Service."""

    async def is_closed(self, client: T) -> bool:
        """Returns whether the client state is closed or released."""
        ...

    async def release(self, client: T) -> None:
        """Closes or releases the client."""
        ...

    async def new(self) -> T:
        """Creates a new client."""
        ...


class AtomicAdapter(Adapter[T], typing.Protocol[T]):
    """Represents an Adapter to a Specific Service that can perform atomic operations."""

    def begin(self, client: T) -> None:
        """Starts an atomic operation."""
        ...

    def commit(self, client: T) -> None:
        """Commits an atomic operation."""
        ...

    def rollback(self, client: T) -> None:
        """Rolls back an atomic operation."""
        ...

    def in_atomic(self, client: T) -> bool:
        """Returns whether the client is currently in an atomic operation."""
        ...


class AtomicAsyncAdapter(AsyncAdapter[T], typing.Protocol[T]):
    """Represents an Adapter to a Specific Service that can perform atomic operations."""

    async def begin(self, client: T) -> None:
        """Starts an atomic operation."""
        ...

    async def commit(self, client: T) -> None:
        """Commits an atomic operation."""
        ...

    async def rollback(self, client: T) -> None:
        """Rolls back an atomic operation."""
        ...

    async def in_atomic(self, client: T) -> bool:
        """Returns whether the client is currently in an atomic operation."""
        ...
