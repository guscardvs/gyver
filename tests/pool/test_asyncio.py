import asyncio
from typing import Coroutine

import pytest
from gyver.attrs import define

from gyver.pools import AsyncPool


@define(frozen=False)
class MockResource:
    state: int
    active: bool

    async def close(self):
        await asyncio.sleep(0.1)
        self.active = False

    @classmethod
    async def create(cls, state: int):
        await asyncio.sleep(0.1)
        return cls(state, True)


def get_factory():
    state = 1

    async def _factory():
        nonlocal state
        result = await MockResource.create(state)
        state += 1
        return result

    return _factory


@pytest.fixture
async def async_pool():
    pool = AsyncPool(get_factory(), MockResource.close)
    yield pool
    await pool.dispose()


async def test_pool_acquire(async_pool: AsyncPool[MockResource]):
    resource = await async_pool.acquire()

    assert resource.state == 1


async def test_pool_release(async_pool: AsyncPool[MockResource]):
    resource = await async_pool.acquire()

    await async_pool.release(resource)

    next_resource = await async_pool.acquire()

    assert next_resource is resource


async def test_pool_prefill(async_pool: AsyncPool[MockResource]):
    await async_pool.prefill(3)

    assert async_pool.resources.qsize() == 3

    await async_pool.prefill(1000)

    assert async_pool.resources.qsize() == 10


async def test_dispose():
    pool = AsyncPool(get_factory(), MockResource.close)

    await pool.prefill(3)
    resources = [await pool.acquire() for _ in range(pool.resources.qsize())]
    for item in resources:
        await pool.release(item)
    await pool.dispose()

    for item in resources:
        assert not item.active


async def delay_coroutine(delay: float, coro: Coroutine):
    await asyncio.sleep(delay)
    return await coro


async def test_async_pool_racing_condition():
    pool = AsyncPool(get_factory(), MockResource.close, pool_size=2)
    # Acquire the only resource available
    r1 = await pool.acquire()

    # Set up a timer to release the resource after a short delay
    task = asyncio.create_task(delay_coroutine(0.5, pool.release(r1)))

    # At the same time, try to acquire a new resource
    # This should result in a race condition
    r2 = await pool.acquire()

    # Wait for the timer to release the first resource
    await task

    # Both resources should be different objects
    assert r1 != r2

    # The pool should still only have one available resource
    assert pool._available == 1

    # Release the second resource
    await pool.release(r2)

    # The pool should now have two available resources
    assert pool._available == 2


async def test_async_pool_recycle():
    # Create a pool with a pool_recycle timeout of 0.2 seconds
    pool = AsyncPool(get_factory(), MockResource.close, pool_size=2, pool_recycle=0.2)

    # Acquire a resource and mark its state
    r1 = await pool.acquire()
    state = r1.state

    # Release the resource and immediately acquire a new one
    await pool.release(r1)
    r2 = await pool.acquire()

    # The new resource should have the same state from the previous one
    # if not expired
    assert r2.state == state
    await pool.release(r2)

    # Wait for the pool_recycle timeout to expire
    await asyncio.sleep(0.3)

    # Acquire a new resource and check its state
    r3 = await pool.acquire()

    # The new resource should be recycled and have a new state
    assert r3.state != state
    assert not r1.active

    # Release all resources and dispose of the pool
    await pool.release(r3)
    await pool.dispose()
