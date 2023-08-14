import typing

import sqlalchemy.ext.asyncio as sa_asyncio

from gyver import context
from gyver.utils import lazyfield

AsyncSaContext = context.AsyncContext[sa_asyncio.AsyncConnection]

AsyncSessionContext = context.AsyncContext[sa_asyncio.AsyncSession]


class AsyncConnectionAdapter(context.AtomicAsyncAdapter[sa_asyncio.AsyncConnection]):
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
        assert self._uri
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
        if trx := (client.get_nested_transaction() or client.get_transaction()):
            await trx.commit()

    async def rollback(self, client: sa_asyncio.AsyncConnection) -> None:
        if trx := (client.get_nested_transaction() or client.get_transaction()):
            await trx.rollback()

    async def in_atomic(self, client: sa_asyncio.AsyncConnection) -> bool:
        return client.in_transaction()

    def context(
        self,
    ) -> "AsyncSaContext":
        return AsyncSaContext(self)


class AsyncSessionAdapter(context.AtomicAsyncAdapter[sa_asyncio.AsyncSession]):
    def __init__(
        self, adapter: context.AtomicAsyncAdapter[sa_asyncio.AsyncConnection]
    ) -> None:
        self._internal_adapter = adapter

    async def new(self):
        return sa_asyncio.AsyncSession(await self._internal_adapter.new())

    async def release(self, client: sa_asyncio.AsyncSession) -> None:
        await client.close()
        await self._internal_adapter.release(client.bind)  # type: ignore

    async def is_closed(self, client: sa_asyncio.AsyncSession) -> bool:
        # sqlalchemy session is never truly closed
        return await self._internal_adapter.is_closed(client.bind)  # type: ignore

    async def begin(self, client: sa_asyncio.AsyncSession) -> None:
        await self._internal_adapter.begin(client.bind)  # type: ignore

    async def commit(self, client: sa_asyncio.AsyncSession) -> None:
        await self._internal_adapter.commit(client.bind)  # type: ignore

    async def rollback(self, client: sa_asyncio.AsyncSession) -> None:
        await self._internal_adapter.rollback(client.bind)  # type: ignore

    async def in_atomic(self, client: sa_asyncio.AsyncSession) -> bool:
        return client.in_transaction()

    def context(
        self,
    ) -> "AsyncSessionContext":
        return AsyncSessionContext(self)
