from gyver.context.atomic_context import (
    AtomicContext,
    AtomicAsyncContext,
    atomic,
)
from gyver.context.context import AsyncContext, Context
from .mocks import MockAdapter, MockAsyncAdapter


def test_atomic_context_acquire_release():
    # Create an instance of AtomicContext
    context = AtomicContext(MockAdapter())

    # Test that `acquire` and `release` work as expected
    client = context.acquire()
    assert client.count == 1
    context.release()
    assert client.count == 0


async def test_atomic_async_context_acquire_release():

    # Create an instance of AtomicAsyncContext
    context = AtomicAsyncContext(MockAsyncAdapter())

    # Test that `acquire` and `release` work as expected
    client = await context.acquire()
    assert client.count == 1
    await context.release()
    assert client.count == 0


def test_atomic_function_works_as_expected_with_context():
    context = Context(MockAdapter())
    with atomic(context) as client:
        assert not client.closed
        assert client.count == 1
    assert client.closed
    assert client.count == 0


async def test_atomic_function_works_as_expected_with_async_context():
    context = AsyncContext(MockAsyncAdapter())
    async with atomic(context) as client:
        assert not client.closed
        assert client.count == 1
    assert client.closed
    assert client.count == 0
