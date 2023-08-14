from contextlib import suppress
from functools import wraps
from typing import cast

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncConnection

from gyver.context import AsyncContext
from gyver.context import atomic
from gyver.database.context.asyncio import AsyncConnectionAdapter
from gyver.database.context.asyncio import AsyncSessionAdapter
from tests.database.context.signal import Signal

sqlite_uri = "sqlite+aiosqlite:///:memory:"


async def test_sqlalchemy_async_adapter_works_correctly_with_default_context():
    adapter = AsyncConnectionAdapter(uri=sqlite_uri)
    context = AsyncContext(adapter)

    async with context.begin() as conn:
        result = await conn.execute(sa.text("SELECT 1"))
        response = result.first()
        assert response
        (first,) = response
        assert first == 1


async def test_sqlalchemy_async_adapter_works_correctly_with_sa_context():
    adapter = AsyncConnectionAdapter(uri=sqlite_uri)
    context = adapter.context()

    async with context.begin() as conn:
        result = await conn.execute(sa.text("SELECT 1"))
        response = result.first()
        assert response
        (first,) = response
        assert first == 1
    assert conn.closed


async def test_sqlalchemy_async_adapter_works_correctly_with_sa_context_transaction():  # noqa
    adapter = AsyncConnectionAdapter(uri=sqlite_uri)
    context = adapter.context()

    async with context.open():
        async with atomic(context) as conn:
            result = await conn.execute(sa.text("SELECT 1"))
            response = result.first()
            assert response
            assert conn.in_transaction()
            assert not conn.in_nested_transaction()
            (first,) = response
            assert first == 1

    async with atomic(context):
        async with context.begin() as conn:
            assert conn.in_transaction()
            assert not conn.in_nested_transaction()

    async with atomic(context):
        async with atomic(context) as conn:
            assert conn.in_transaction()
            assert conn.in_nested_transaction()
        assert conn.in_transaction()
        assert not conn.in_nested_transaction()


async def test_sqlalchemy_async_adapter_works_correctly_with_sa_acquire_session():  # noqa
    adapter = AsyncConnectionAdapter(uri=sqlite_uri)
    context = AsyncSessionAdapter(adapter).context()

    async with context as session:
        result = await session.execute(sa.text("SELECT 1"))
        response = result.first()
        assert response
        (first,) = response
        assert first == 1


async def test_sqlalchemy_context_and_adapter_are_compliant_to_atomic():
    adapter = AsyncConnectionAdapter(uri=sqlite_uri)
    context = adapter.context()

    async with atomic(context) as client:
        result = await client.execute(sa.text("SELECT 1"))
        response = result.first()
        assert response
        (first,) = response
        assert first == 1
        assert await adapter.in_atomic(client)
    assert not await adapter.in_atomic(client)


async def test_sqlalchemy_session_and_adapter_are_compliant_to_atomic():
    adapter = AsyncSessionAdapter(AsyncConnectionAdapter(uri=sqlite_uri))
    context = adapter.context()

    async with atomic(context) as client:
        result = await client.execute(sa.text("SELECT 1"))
        response = result.first()
        assert response
        (first,) = response
        assert first == 1
        assert await adapter.in_atomic(client)
    assert not await adapter.in_atomic(client)

    async with atomic(context):
        async with atomic(context) as client:
            bound = cast(AsyncConnection, client.bind)
            assert bound.in_transaction()
            assert bound.in_nested_transaction()
        assert bound.in_transaction()
        assert not bound.in_nested_transaction()


class MockException(Exception):
    pass


def make_rollback(func, signal: Signal):
    @wraps(func)
    async def rollback(*args, **kwargs):
        signal.do()
        return await func(*args, **kwargs)

    return rollback


async def test_transaction_did_rollback_with_atomic():
    adapter = AsyncConnectionAdapter(uri=sqlite_uri)
    context = adapter.context()
    signal = Signal()
    with suppress(MockException):
        async with atomic(context):
            adapter.rollback = make_rollback(adapter.rollback, signal)
            raise MockException
    assert signal.did


async def test_transaction_did_rollback_with_atomic_session():
    adapter = AsyncSessionAdapter(AsyncConnectionAdapter(uri=sqlite_uri))
    context = adapter.context()
    signal = Signal()
    with suppress(MockException):
        async with atomic(context):
            adapter.rollback = make_rollback(adapter.rollback, signal)
            raise MockException
    assert signal.did
