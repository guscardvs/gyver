import sqlalchemy as sa

from gyver.context import AsyncContext
from gyver.database.context.asyncio import AsyncSaAdapter

sqlite_uri = "sqlite+aiosqlite:///:memory:"


async def test_sqlalchemy_async_adapter_works_correctly_with_default_context():
    adapter = AsyncSaAdapter(uri=sqlite_uri)
    context = AsyncContext(adapter)

    async with context.begin() as conn:
        result = await conn.execute(sa.text("SELECT 1"))
        response = result.first()
        assert response
        (first,) = response
        assert first == 1


async def test_sqlalchemy_async_adapter_works_correctly_with_sa_context():
    adapter = AsyncSaAdapter(uri=sqlite_uri)
    context = adapter.context()

    async with context.begin() as conn:
        result = await conn.execute(sa.text("SELECT 1"))
        response = result.first()
        assert response
        (first,) = response
        assert first == 1


async def test_sqlalchemy_async_adapter_works_correctly_with_sa_context_transaction():  # noqa
    adapter = AsyncSaAdapter(uri=sqlite_uri)
    context = adapter.context(transaction_on="begin")

    async with context.open():
        async with context.begin() as conn:
            result = await conn.execute(sa.text("SELECT 1"))
            response = result.first()
            assert response
            assert conn.in_transaction()
            assert not conn.in_nested_transaction()
            (first,) = response
            assert first == 1

    context = adapter.context(transaction_on="open")
    async with context.open():
        async with context.begin() as conn:
            assert conn.in_transaction()
            assert not conn.in_nested_transaction()


async def test_sqlalchemy_async_adapter_works_correctly_with_sa_acquire_session():  # noqa
    adapter = AsyncSaAdapter(uri=sqlite_uri)
    context = adapter.context()

    async with context.acquire_session() as session:
        result = await session.execute(sa.text("SELECT 1"))
        response = result.first()
        assert response
        (first,) = response
        assert first == 1
