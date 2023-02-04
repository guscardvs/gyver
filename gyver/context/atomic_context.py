from typing import Generic, Union, overload

from gyver.utils.lazy import lazyfield
from .interfaces.adapter import AtomicAdapter, AtomicAsyncAdapter
from .context import Context, AsyncContext
from .typedef import T


class AtomicContext(Context[T], Generic[T]):
    adapter: AtomicAdapter[T]

    def __init__(self, adapter: AtomicAdapter[T]) -> None:
        super().__init__(adapter)

    @lazyfield
    def client(self):
        return self.adapter.new()

    def acquire(self):
        client = super().acquire()
        self.adapter.begin(client)
        return client

    def release(self):
        self.adapter.end(self.client)
        return super().release()


class AtomicAsyncContext(AsyncContext[T], Generic[T]):
    adapter: AtomicAsyncAdapter[T]

    def __init__(self, adapter: AtomicAsyncAdapter[T]) -> None:
        super().__init__(adapter)

    async def acquire(self):
        client = await super().acquire()
        await self.adapter.begin(client)
        return client

    async def release(self):
        if self._client is None:
            raise RuntimeError(
                "Release should not be called before client initialization"
            )
        await self.adapter.end(self._client)
        return await super().release()


@overload
def atomic(context: Context[T]) -> AtomicContext[T]:
    ...


@overload
def atomic(context: AsyncContext[T]) -> AtomicAsyncContext[T]:
    ...


def atomic(
    context: Union[Context[T], AsyncContext[T]]
) -> Union[AtomicContext[T], AtomicAsyncContext[T]]:
    required_methods = {"begin", "end"}
    adapter_methods = set(dir(context.adapter))

    if not required_methods.issubset(adapter_methods):
        raise ValueError(
            f"The adapter does not have required methods {required_methods}"
        )

    return (
        AtomicContext(context.adapter)  # type: ignore
        if isinstance(context, Context)
        else AtomicAsyncContext(context.adapter)  # type: ignore
    )
