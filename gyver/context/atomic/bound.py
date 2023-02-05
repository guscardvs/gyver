from .core import AtomicContext, AsyncAtomicContext
from gyver.context.context import Context, AsyncContext
from gyver.context.typedef import T
from gyver.context.interfaces.adapter import AtomicAdapter, AtomicAsyncAdapter
from typing import Generic


class BoundContext(AtomicContext[T], Generic[T]):
    adapter: AtomicAdapter[T]

    def __init__(self, adapter: AtomicAdapter[T], context: Context[T]) -> None:
        super().__init__(adapter)
        self._context = context

    def acquire(self):
        with self._lock:
            client = self._context.acquire()
            self._stack += 1
            self.adapter.begin(client)
        return client

    def release(self, commit: bool = True):
        with self._lock:
            if self._stack == 1:
                if self.adapter.in_atomic(self._context.client):
                    if commit:
                        self.adapter.commit(self._context.client)
                    else:
                        self.adapter.rollback(self._context.client)
                self._context.release()
            self._stack -= 1


class AsyncBoundContext(AsyncAtomicContext[T], Generic[T]):
    adapter: AtomicAsyncAdapter[T]

    def __init__(
        self, adapter: AtomicAsyncAdapter[T], context: AsyncContext[T]
    ) -> None:
        super().__init__(adapter)
        self._context = context

    async def acquire(self):
        async with self._lock:
            client = await self._context.acquire()
            if self.stack == 0:
                await self.adapter.begin(client)
            self._stack += 1
            return client

    async def release(self, commit: bool = True):
        async with self._lock:
            if self._context._client is None:
                raise RuntimeError(
                    "Release should not be called before client initialization"
                )
            if self._stack == 1:
                if commit:
                    await self.adapter.commit(self._context._client)
                else:
                    await self.adapter.rollback(self._context._client)
            self._stack -= 1
        await self._context.release()
