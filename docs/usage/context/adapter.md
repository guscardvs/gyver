# The Adapter Interface

[gyver.context][] provides four adapter interfaces, each catering to different paradigms as required.

## Adapter
!!! note inline end "Asyncio"
    In an asyncio context, you can use the [AsyncAdapter][gyver.context] instead, which requires the same methods but in an `async def` version.

The [Adapter][gyver.context] interface serves as a foundation for managing simple synchronous resources. It defines the following required methods:

- [is_closed][gyver.context.Adapter]: This method checks the status of the resource. In cases where certain resources lack an explicit API for checking openness, returning `False` is acceptable.
- [new][gyver.context.Adapter]: Acquires a new resource. It should create a new resource and return it using synchronous programming paradigms.
- [release][gyver.context.Adapter]: Releases a resource.
  

## AtomicAdapter
!!! note inline end "Asyncio and Adapter"
    Both AtomicAdapter and AtomicAsyncAdapter share the same interface, with `async def` versions for AtomicAsyncAdapter's methods. Furthermore, AtomicAdapter and AtomicAsyncAdapter inherit from their respective Adapter counterparts, requiring compliance with both interfaces.

The [AtomicAdapter][gyver.context] interface extends the Adapter interface to include support for synchronous resource management with atomicity. It encompasses methods for managing atomic operations and their outcomes:

- [begin][gyver.context.AtomicAdapter]: Initializes an atomic operation.
- [commit][gyver.context.AtomicAdapter]: Commits the current atomic operation.
- [rollback][gyver.context.AtomicAdapter]: Rolls back the current atomic operation.
- [in_atomic][gyver.context.AtomicAdapter]: Indicates whether the current resource is involved in an atomic operation.


## Sync Example

### Adapter

In this example, we'll demonstrate how to create a synchronous adapter using the `gyver.context` module. This adapter manages a requests session, highlighting the process of acquiring and releasing resources within a context.

```python
import requests
from gyver.context import Context

class SessionAdapter:
    def new(self):
        """
        Create a new requests session.
        """
        return requests.Session()
    
    def release(self, client: requests.Session):
        """
        Release the requests session by closing it.
        """
        client.close()
    
    def is_closed(self, client: requests.Session) -> bool:
        """
        Check if the requests session is closed.
        Since requests does not have an explicit way to check session status,
        we assume it's never closed and return False.
        """
        return False

# Create a context using the SessionAdapter
session_context = Context(SessionAdapter())
```

### AtomicAdapter

In this example, we'll illustrate how to implement an atomic adapter using the `gyver.context` module. This adapter integrates with SQLAlchemy to manage database connections within a transactional context.

```python
import typing

import sqlalchemy as sa
import sqlalchemy.engine as sa_engine

from gyver import context
from gyver.utils import lazyfield

SaContext = context.Context[sa_engine.Connection]


class SaAdapter(context.Adapter[sa_engine.Connection]):
    """
    A synchronous adapter for managing SQLAlchemy connections within a transactional context.
    """

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
        engine: sa_engine.Engine,
    ) -> None:
        ...

    def __init__(
        self,
        *,
        uri: typing.Optional[str] = None,
        engine: typing.Optional[sa_engine.Engine] = None,
    ) -> None:
        if not any((uri, engine)):
            raise TypeError("Missing parameters (uri/engine)")
        self._uri = uri
        if engine is not None:
            self._engine = engine

    @lazyfield
    def _engine(self):
        assert self._uri
        return sa.create_engine(self._uri)

    def is_closed(self, client: sa_engine.Connection) -> bool:
        """
        Check if the database connection is closed.
        """
        return client.closed

    def new(self):
        """
        Create a new database connection.
        """
        return self._engine.connect()

    def release(self, client: sa_engine.Connection) -> None:
        """
        Release the database connection.
        """
        client.close()

    def begin(self, client: sa_engine.Connection) -> None:
        """
        Begin a transaction.
        """
        if client.in_transaction():
            client.begin_nested()
        else:
            client.begin()

    def commit(self, client: sa_engine.Connection) -> None:
        """
        Commit the transaction.
        """
        if trx := (client.get_nested_transaction() or client.get_transaction()):
            trx.commit()

    def rollback(self, client: sa_engine.Connection) -> None:
        """
        Roll back the transaction.
        """
        if trx := (client.get_nested_transaction() or client.get_transaction()):
            trx.rollback()

    def in_atomic(self, client: sa_engine.Connection) -> bool:
        """
        Check if the connection is within an active transaction.
        """
        return client.in_transaction()

    def context(
        self,
    ) -> "SaContext":
        """
        Create a context using the adapter.
        """
        return SaContext(self)
```

## Async Example

### AsyncAdapter

In this example, we'll showcase the implementation of an asynchronous adapter using the `gyver.context` module. The adapter manages asynchronous resources, specifically `aiohttp` client sessions, demonstrating how to acquire and release these resources within an asynchronous context.

```python
import aiohttp
from gyver.context import AsyncContext

class AsyncSessionAdapter:
    async def new(self):
        """
        Create a new aiohttp client session asynchronously.
        """
        return aiohttp.ClientSession()

    async def release(self, client: aiohttp.ClientSession):
        """
        Release the aiohttp client session asynchronously by closing it.
        """
        await client.close()

    async def is_closed(self, client: aiohttp.ClientSession):
        """
        Check if the aiohttp client session is closed asynchronously.
        """
        return client.closed

# Create an asynchronous context using the AsyncSessionAdapter
async_session_context = AsyncContext(AsyncSessionAdapter())
```

### AtomicAsyncAdapter

In this example, we'll demonstrate the implementation of an `AtomicAsyncAdapter` using SQLAlchemy's asynchronous features. This adapter allows you to manage asynchronous database connections and transactions seamlessly using the `gyver.context` module.


```python
import typing

import sqlalchemy.ext.asyncio as sa_asyncio

from gyver import context
from gyver.utils import lazyfield

AsyncSaContext = context.AsyncContext[sa_asyncio.AsyncConnection]


class AsyncConnectionAdapter(context.AtomicAsyncAdapter[sa_asyncio.AsyncConnection]):    
    """
    An atomic asynchronous adapter for managing SQLAlchemy connections and transactions.
    """
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
        """
        Check if the asynchronous database connection is closed.
        """
        return client.closed

    async def release(self, client: sa_asyncio.AsyncConnection) -> None:
        """
        Release the asynchronous database connection.
        """
        return await client.close()

    async def new(self) -> sa_asyncio.AsyncConnection:
        """
        Create a new asynchronous database connection.
        """
        return await self._create_connection()

    async def begin(self, client: sa_asyncio.AsyncConnection) -> None:
        """
        Begin an asynchronous transaction.
        """
        if client.in_transaction():
            await client.begin_nested()
        else:
            await client.begin()

    async def commit(self, client: sa_asyncio.AsyncConnection) -> None:
        """
        Commit the asynchronous transaction.
        """
        if trx := (client.get_nested_transaction() or client.get_transaction()):
            await trx.commit()

    async def rollback(self, client: sa_asyncio.AsyncConnection) -> None:
        """
        Roll back the asynchronous transaction.
        """
        if trx := (client.get_nested_transaction() or client.get_transaction()):
            await trx.rollback()

    async def in_atomic(self, client: sa_asyncio.AsyncConnection) -> bool:
        """
        Check if the asynchronous connection is within an active transaction.
        """
        return client.in_transaction()

    def context(
        self,
    ) -> AsyncSaContext:
        """
        Create a context using the adapter.
        """
        return AsyncSaContext(self)

# Create an asynchronous context using the AsyncConnectionAdapter
async_sa_context = AsyncSaContext(AsyncConnectionAdapter())
```

In these examples, we demonstrate how to create different types of adapters and contexts using the gyver.context module for both synchronous and asynchronous resource management. This approach allows for efficient and flexible resource handling in various programming paradigms.