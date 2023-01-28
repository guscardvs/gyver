import asyncio
import pytest

from .mocks import MockAsyncAdapter
from gyver.context import AsyncContext


async def test_asynccontext_acquisition():
    adapter = MockAsyncAdapter()
    context = AsyncContext(adapter)
    async with context.open():
        assert context.stack == 1
        client = await context.acquire()
        assert not client.closed
        client2 = await context.acquire()
        assert client == client2
        await context.release()
        await context.release()
    assert context.stack == 0
    assert client.closed


async def test_asynccontext_release():
    adapter = MockAsyncAdapter()
    context = AsyncContext(adapter)
    client = await context.acquire()
    assert not client.closed
    await context.release()
    assert context.stack == 0
    assert client.closed


async def test_asynccontext_double_release():
    adapter = MockAsyncAdapter()
    context = AsyncContext(adapter)
    client = await context.acquire()
    assert not client.closed
    await context.release()
    assert context.stack == 0
    assert client.closed
    with pytest.raises(RuntimeError):
        await context.release()


async def test_context_multi_threading():
    adapter = MockAsyncAdapter()
    context = AsyncContext(adapter)

    async def worker():
        async with context.open():
            async with context.begin() as client:
                assert context.stack == 2
                assert not client.closed
                client2 = await context.acquire()
                assert client == client2
                await context.release()
        assert context.stack == 0
        assert client.closed

    tasks = []
    for _ in range(5):
        tasks.append(asyncio.create_task(worker()))
    await asyncio.gather(*tasks)
