import threading
import time

import pytest
from gyver.attrs import define

from gyver.pools import ThreadPool


@define(frozen=False)
class MockResource:
    state: int
    active: bool

    def close(self):
        time.sleep(0.1)
        self.active = False

    @classmethod
    def create(cls, state: int):
        time.sleep(0.1)
        return cls(state, True)


def get_factory():
    state = 1

    def _factory():
        nonlocal state
        result = MockResource.create(state)
        state += 1
        return result

    return _factory


@pytest.fixture
def thread_pool():
    pool = ThreadPool(get_factory(), MockResource.close)
    yield pool
    pool.dispose()


def test_pool_acquire(thread_pool):
    resource = thread_pool.acquire()

    assert resource.state == 1


def test_pool_release(thread_pool):
    resource = thread_pool.acquire()

    thread_pool.release(resource)

    next_resource = thread_pool.acquire()

    assert next_resource is resource


def test_pool_prefill(thread_pool):
    thread_pool.prefill(3)

    assert thread_pool.resources.qsize() == 3

    thread_pool.prefill(1000)

    assert thread_pool.resources.qsize() == 10


def test_dispose():
    pool = ThreadPool(get_factory(), MockResource.close)

    pool.prefill(3)
    resources = [pool.acquire() for _ in range(pool.resources.qsize())]
    for item in resources:
        pool.release(item)
    pool.dispose()

    for item in resources:
        assert not item.active


def test_thread_pool_racing_condition():
    pool = ThreadPool(get_factory(), MockResource.close, pool_size=2)

    # Define a worker function
    def worker():
        time.sleep(0.1)

    # Acquire the only thread available
    t1 = pool.acquire()

    # Set up a timer to release the thread after a short delay
    timer = threading.Timer(0.5, pool.release, args=[t1])
    timer.start()

    # At the same time, try to acquire a new thread
    # This should result in a race condition
    t2 = pool.acquire()

    # Wait for the timer to release the first thread
    timer.join()

    # Both threads should be different objects
    assert t1 != t2

    # The pool should still only have one available thread
    assert pool._available == 1

    # Release the second thread
    pool.release(t2)

    # The pool should now have two available threads
    assert pool._available == 2


def test_thread_pool_recycle():
    # Create a pool with a pool_recycle timeout of 0.2 seconds
    pool = ThreadPool(get_factory(), MockResource.close, pool_size=2, pool_recycle=0.2)

    # Acquire a resource and mark its state
    t1 = pool.acquire()
    state = t1.state

    # Release the resource and immediately acquire a new one
    pool.release(t1)
    t2 = pool.acquire()

    # The new resource should have the same state from the previous one
    # if not expired
    assert t2.state == state
    pool.release(t2)

    # Wait for the pool_recycle timeout to expire
    time.sleep(0.3)

    # Acquire a new resource and check its state
    t3 = pool.acquire()

    # The new resource should be recycled and have a new state
    assert t3.state != state
    assert not t1.active

    # Release all resources and dispose of the pool
    pool.release(t3)
    pool.dispose()
