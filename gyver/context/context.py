import asyncio
import contextlib
import threading
import typing

from gyver.utils import lazyfield

from . import interfaces
from .typedef import T


class Context(typing.Generic[T]):
    def __init__(self, adapter: interfaces.Adapter[T]) -> None:
        """
        Initialize a new Context.
        :param adapter: An adapter that will be used to acquire and release resources.
        """
        self._adapter = adapter
        self._stack = 0  # Keeps track of how many frames are using this context
        self._lock = threading.Lock()  # A lock to ensure thread safety

    @lazyfield
    def client(self) -> T:
        """
        Returns the current resource being used by the context.
        Acquires a new resource if the current one is closed or doesn't exist.
        """
        return self.adapter.new()

    @property
    def stack(self):
        """
        Returns how many frames are using this context
        """
        return self._stack

    @property
    def adapter(self) -> interfaces.Adapter[T]:
        """
        Returns the adapter that is being used by this context
        """
        return self._adapter

    def is_active(self) -> bool:
        """
        Returns whether the context is currently in use
        """
        return self._stack > 0

    def acquire(self):
        """
        Acquires a new resource from the adapter and increases the stack count.
        """
        with self._lock:
            if self.adapter.is_closed(self.client):
                Context.client.cleanup(self)
            self._stack += 1
            return self.client

    def release(self):
        """
        Releases the current resource if the stack count is 1,
        and decreases the stack count.
        """
        with self._lock:
            if self._stack == 1:
                self.adapter.release(self.client)
                Context.client.cleanup(self)
            self._stack -= 1

    @contextlib.contextmanager
    def open(self):
        """
        A context manager that acquires and releases resources without returning it.
        """
        with self:
            yield

    @contextlib.contextmanager
    def begin(self):
        """
        A context manager that acquires and releases resources and returns it.
        """
        with self as client:
            yield client

    def __enter__(self):
        """
        Acquires a new resource from the adapter and increases the stack count.
        """
        return self.acquire()

    def __exit__(self, *_):
        """
        Releases the current resource if the stack count is 1,
         and decreases the stack count.
        """
        self.release()


class AsyncContext(typing.Generic[T]):
    def __init__(self, adapter: interfaces.AsyncAdapter[T]) -> None:
        """
        Initialize a new AsyncContext.
        :param adapter: An async adapter that will be used to acquire
        and release resources.
        """
        self._adapter = adapter
        self._stack = 0  # Keeps track of how many frames are using this context
        self._client: typing.Optional[T] = None  # The current resource being used
        self._lock = asyncio.Lock()  # A lock to ensure thread safety

    @property
    def stack(self) -> int:
        """
        Returns how many frames are using this context
        """
        return self._stack

    @property
    def adapter(self) -> interfaces.AsyncAdapter[T]:
        """
        Returns the adapter that is being used by this context
        """
        return self._adapter

    def is_active(self) -> bool:
        """
        Returns whether the context is currently in use
        """
        return self._stack > 0

    async def client(self) -> T:
        """
        Returns the current resource being used by the context.
        Acquires a new resource if the current one is closed or doesn't exist.
        """
        if self._client is None or await self._adapter.is_closed(self._client):
            self._client = await self._adapter.new()
        return self._client

    async def acquire(self):
        """
        Acquires a new resource from the adapter and increases the stack count.
        """
        async with self._lock:
            client = await self.client()
            self._stack += 1
            return client

    async def release(self):
        """
        Releases the current resource if the stack count is 1,
        and decreases the stack count.
        """
        async with self._lock:
            if self._client is None:
                raise RuntimeError(
                    "Release should not be called before client initialization"
                )
            if self._stack == 1:
                await self.adapter.release(self._client)
                self._client = None
            self._stack -= 1

    @contextlib.asynccontextmanager
    async def open(self):
        """
        An async context manager that acquires
        and releases resources without returning it.
        """
        async with self:
            yield

    @contextlib.asynccontextmanager
    async def begin(self):
        """
        An async context manager that acquires and releases resources and returns it.
        """
        async with self as client:
            yield client

    async def __aenter__(self):
        """
        Acquires a new resource from the adapter and increases the stack count.
        """
        return await self.acquire()

    async def __aexit__(self, *_):
        """
        Releases the current resource if the stack count
        is 1, and decreases the stack count.
        """
        await self.release()
