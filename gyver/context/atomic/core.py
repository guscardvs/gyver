from typing import Generic

from gyver.utils import lazyfield
from gyver.context.interfaces.adapter import AtomicAdapter, AtomicAsyncAdapter
from gyver.context.context import Context, AsyncContext
from gyver.context.typedef import T


class AtomicContext(Context[T], Generic[T]):
    adapter: AtomicAdapter[T]

    def __init__(self, adapter: AtomicAdapter[T]) -> None:
        super().__init__(adapter)

    @lazyfield
    def client(self):
        return self.adapter.new()

    def acquire(self):
        with self._lock:
            if self.adapter.is_closed(self.client):
                AtomicContext.client.cleanup(self)
            self._stack += 1
            self.adapter.begin(self.client)
        return self.client

    def release(self, commit: bool = True):
        with self._lock:
            if self._stack == 1:
                if self.adapter.in_atomic(self.client):
                    if commit:
                        self.adapter.commit(self.client)
                    else:
                        self.adapter.rollback(self.client)
                self.adapter.release(self.client)
                Context.client.cleanup(self)
            self._stack -= 1

    def __exit__(self, *exc):
        self.release(not any(exc))


class AsyncAtomicContext(AsyncContext[T], Generic[T]):
    adapter: AtomicAsyncAdapter[T]

    def __init__(self, adapter: AtomicAsyncAdapter[T]) -> None:
        super().__init__(adapter)

    async def acquire(self):
        async with self._lock:
            client = await self.client()
            if self.stack == 0:
                await self.adapter.begin(client)
            self._stack += 1
            return client

    async def release(self, commit: bool = True):
        async with self._lock:
            if self._client is None:
                raise RuntimeError(
                    "Release should not be called before client initialization"
                )
            if self._stack == 1:
                if await self.adapter.in_atomic(self._client):
                    if commit:
                        await self.adapter.commit(self._client)
                    else:
                        await self.adapter.rollback(self._client)
                await self.adapter.release(self._client)
                self._client = None
            self._stack -= 1

    async def __aexit__(self, *exc):
        await self.release(not any(exc))
