from typing import Generic

from gyver.context.context import AsyncContext
from gyver.context.context import Context
from gyver.context.interfaces.adapter import AtomicAdapter
from gyver.context.interfaces.adapter import AtomicAsyncAdapter
from gyver.context.typedef import T


class BoundContext(Context[T], Generic[T]):
    """A context manager for managing atomic transactions with an adapter."""

    adapter: AtomicAdapter[T]

    def __init__(self, adapter: AtomicAdapter[T], context: Context[T]) -> None:
        """
        Initialize a BoundContext instance.

        Args:
            adapter (AtomicAdapter[T]): The atomic adapter for managing transactions.
            context (Context[T]): The underlying context to manage.
        """
        super().__init__(adapter)
        self._context = context

    def acquire(self):
        """
        Acquire the context for a transaction and begin an atomic operation.

        Returns:
            T: The acquired context.
        """
        with self._lock:
            client = self._context.acquire()
            self._stack += 1
            self.adapter.begin(client)
        return client

    def release(self, commit: bool = True):
        """
        Release the context, committing or rolling back the transaction if needed.

        Args:
            commit (bool, optional): Whether to commit the transaction. Defaults to True.
        """
        with self._lock:
            if self._stack == 1:
                if self.adapter.in_atomic(self._context.client):
                    if commit:
                        self.adapter.commit(self._context.client)
                    else:
                        self.adapter.rollback(self._context.client)
                self._context.release()
            self._stack -= 1

    def __exit__(self, *exc):
        """
        Exit the context manager and release the context.

        Args:
            *exc: Exception information.
        """
        self.release(not any(exc))


class AsyncBoundContext(AsyncContext[T], Generic[T]):
    """An asynchronous context manager for managing atomic transactions with an async adapter."""

    adapter: AtomicAsyncAdapter[T]

    def __init__(
        self, adapter: AtomicAsyncAdapter[T], context: AsyncContext[T]
    ) -> None:
        """
        Initialize an AsyncBoundContext instance.

        Args:
            adapter (AtomicAsyncAdapter[T]): The async atomic adapter for managing transactions.
            context (AsyncContext[T]): The underlying async context to manage.
        """
        super().__init__(adapter)
        self._context = context

    async def acquire(self):
        """
        Acquire the async context for a transaction and begin an atomic operation.

        Returns:
            T: The acquired async context.
        """
        async with self._lock:
            client = await self._context.acquire()
            if self._stack == 0:
                await self.adapter.begin(client)
            self._stack += 1
            return client

    async def release(self, commit: bool = True):
        """
        Release the async context, committing or rolling back the transaction if needed.

        Args:
            commit (bool, optional): Whether to commit the transaction. Defaults to True.
        """
        async with self._lock:
            client = await self._context.client()
            if self._stack == 1:
                if commit:
                    await self.adapter.commit(client)
                else:
                    await self.adapter.rollback(client)
            self._stack -= 1
        await self._context.release()

    async def __aexit__(self, *exc):
        """
        Exit the async context manager and release the async context.

        Args:
            *exc: Exception information.
        """
        await self.release(not any(exc))
