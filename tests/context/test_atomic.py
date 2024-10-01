import asyncio
import threading

from gyver.context.atomic_ import AsyncAtomicContext
from gyver.context.atomic_ import AtomicContext
from gyver.context.atomic_ import atomic
from gyver.context.context import AsyncContext
from gyver.context.context import Context

from .mocks import MockAdapter
from .mocks import MockAsyncAdapter


def test_atomic_context_acquire_release():
    # Create an instance of AtomicContext
    context = AtomicContext(MockAdapter())

    # Test that `acquire` and `release` work as expected
    client = context.acquire()
    assert client.count == 1
    context.release()
    assert client.count == 0


def test_atomic_context_multi_threading():
    adapter = MockAdapter()
    context = atomic(Context(adapter), bound=False)

    def worker():
        with context.open():
            with context.begin() as client:
                assert context.stack == 2
                assert not client.closed
                client2 = context.acquire()
                assert client == client2
                context.release()
        assert context.stack == 0

    threads = []
    for _ in range(5):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    assert not context.is_active()


def test_bound_context_client_yields_the_same_client_instantiated_in_context():
    adapter = MockAdapter()
    context = Context(adapter)
    bound_context = atomic(context)
    with context.begin() as ctx_client:
        with bound_context.begin() as bnd_ctx_client:
            assert ctx_client is bnd_ctx_client


async def test_atomic_async_context_acquire_release():
    # Create an instance of AtomicAsyncContext
    context = AsyncAtomicContext(MockAsyncAdapter())

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


async def test_asynccontext_multitask():
    adapter = MockAsyncAdapter()
    context = atomic(AsyncContext(adapter), bound=False)

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


async def test_bound_async_context_client_yields_the_same_client_in_context():
    adapter = MockAsyncAdapter()
    context = AsyncContext(adapter)
    bound_context = atomic(context)
    async with context.begin() as ctx_client:
        async with bound_context.begin() as bnd_ctx_client:
            assert ctx_client is bnd_ctx_client
