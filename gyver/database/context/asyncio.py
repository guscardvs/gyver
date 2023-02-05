import contextlib
import sys
import typing

import sqlalchemy.ext.asyncio as sa_asyncio

from gyver import context
from gyver.context.atomic.resolver import in_atomic
from gyver.utils import lazyfield
from gyver.utils.helpers import deprecated

TransactionOptions = typing.Optional[typing.Literal["open", "begin"]]


class AsyncSaAdapter(context.AtomicAsyncAdapter[sa_asyncio.AsyncConnection]):
    @typing.overload
    def __init__(
        self,
        *,
        uri: str,
        engine: None = None,
    ) -> None:
        ...

    @typing.overload
    def __init__(
        self,
        *,
        uri: None = None,
        engine: sa_asyncio.AsyncEngine,
    ) -> None:
        ...

    def __init__(
        self,
        *,
        uri: typing.Optional[str] = None,
        engine: typing.Optional[sa_asyncio.AsyncEngine] = None,
    ) -> None:
        if not any((uri, engine)):
            raise TypeError("Missing parameters (uri/engine)")
        self._uri = uri
        if engine is not None:
            self._engine = engine

    @lazyfield
    def _engine(self):
        return sa_asyncio.create_async_engine(self._uri)

    def _create_connection(self):
        return self._engine.connect()

    async def is_closed(self, client: sa_asyncio.AsyncConnection) -> bool:
        return client.closed

    async def release(self, client: sa_asyncio.AsyncConnection) -> None:
        return await client.close()

    async def new(self) -> sa_asyncio.AsyncConnection:
        return await self._create_connection()

    async def begin(self, client: sa_asyncio.AsyncConnection) -> None:
        if client.in_transaction():
            await client.begin_nested()
        else:
            await client.begin()

    async def commit(self, client: sa_asyncio.AsyncConnection) -> None:
        if trx := (
            client.get_nested_transaction() or client.get_transaction()
        ):
            await trx.commit()

    async def rollback(self, client: sa_asyncio.AsyncConnection) -> None:
        if trx := (
            client.get_nested_transaction() or client.get_transaction()
        ):
            await trx.rollback()

    async def in_atomic(self, client: sa_asyncio.AsyncConnection) -> bool:
        return client.in_transaction()

    def context(
        self,
        transaction_on: TransactionOptions = "open",
    ) -> "AsyncSaContext":
        return AsyncSaContext(self, transaction_on=transaction_on)

    def session(self):
        return AsyncSessionAdapter(self).context()


if sys.version_info < (3, 10):

    class asyncnullcontext(contextlib.nullcontext):
        async def __aenter__(self):
            return self.enter_result

        async def __aexit__(self, *excinfo):
            pass

else:
    asyncnullcontext = contextlib.nullcontext


class AsyncSaContext(context.AsyncContext[sa_asyncio.AsyncConnection]):
    def __init__(
        self,
        adapter: context.AtomicAsyncAdapter[sa_asyncio.AsyncConnection],
        transaction_on: TransactionOptions = "open",
    ) -> None:
        super().__init__(adapter)
        self._transaction_on = transaction_on

    @deprecated
    def _make_transaction(self):
        return (
            asyncnullcontext()
            if self._transaction_on is None
            else in_atomic(self)
        )

    def open(self):
        if self._transaction_on != "open":
            return super().open()
        return self._transaction_open()

    def begin(self):
        if self._transaction_on != "begin":
            return super().begin()
        return self.transaction_begin()

    @deprecated
    @contextlib.asynccontextmanager
    async def _transaction_open(self):
        async with super().open():
            async with self._make_transaction():
                yield

    @deprecated
    @contextlib.asynccontextmanager
    async def transaction_begin(self):
        async with super().begin() as client:
            async with self._make_transaction():
                yield client

    @contextlib.asynccontextmanager
    async def acquire_session(
        self,
    ) -> typing.AsyncGenerator[sa_asyncio.AsyncSession, None]:
        context = AsyncSessionAdapter(self.adapter).context()  # type: ignore
        async with context as session:
            yield session


class AsyncSessionAdapter(context.AtomicAsyncAdapter[sa_asyncio.AsyncSession]):
    def __init__(
        self, adapter: context.AtomicAsyncAdapter[sa_asyncio.AsyncConnection]
    ) -> None:
        self._internal_adapter = adapter

    async def new(self):
        return sa_asyncio.AsyncSession(await self._internal_adapter.new())

    async def release(self, client: sa_asyncio.AsyncSession) -> None:
        await client.close()
        await self._internal_adapter.release(client.bind)

    async def is_closed(self, client: sa_asyncio.AsyncSession) -> bool:
        # sqlalchemy session is never truly closed
        return await self._internal_adapter.is_closed(client.bind)

    async def begin(self, client: sa_asyncio.AsyncSession) -> None:
        await self._internal_adapter.begin(client.bind)

    async def commit(self, client: sa_asyncio.AsyncSession) -> None:
        await self._internal_adapter.commit(client.bind)

    async def rollback(self, client: sa_asyncio.AsyncSession) -> None:
        await self._internal_adapter.rollback(client.bind)

    async def in_atomic(self, client: sa_asyncio.AsyncSession) -> bool:
        return client.in_transaction()

    def context(
        self,
    ) -> "AsyncSessionContext":
        return AsyncSessionContext(self)


AsyncSessionContext = context.AsyncContext[sa_asyncio.AsyncSession]
