import contextlib
import threading

from gyver.context import Context

from .mocks import MockAdapter


def test_context_acquisition():  # sourcery skip: extract-method
    adapter = MockAdapter()
    context = Context(adapter)
    with context.open():
        with context.begin() as client:
            assert context.stack == 2
            assert not client.closed
            client2 = context.acquire()
            assert context.stack == 3
            assert client == client2
            context.release()
    assert context.stack == 0
    assert client.closed


def test_context_release():
    adapter = MockAdapter()
    context = Context(adapter)
    with context.open():
        client = context.acquire()
        assert not client.closed
        context.release()
        assert context.stack == 1
    assert client.closed
    assert context.stack == 0


def test_context_double_release():
    adapter = MockAdapter()
    context = Context(adapter)
    with context.open():
        client = context.acquire()
        assert not client.closed
        context.release()
        assert context.stack == 1
    assert client.closed
    assert context.stack == 0


def test_context_multi_threading():
    adapter = MockAdapter()
    context = Context(adapter)

    def worker():
        with context.open():
            with context.begin() as client:
                assert context.stack == 2
                assert not client.closed
                client2 = context.acquire()
                assert client == client2
                context.release()
        assert context.stack == 0
        assert client.closed

    threads = []
    for _ in range(5):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


def test_context_releases_resource_even_on_error():
    # sourcery skip: raise-specific-error
    adapter = MockAdapter()
    context = Context(adapter)

    with contextlib.suppress(Exception):
        with context.begin() as client:
            raise Exception

    assert client.closed  # type: ignore
    assert context.stack == 0

    with contextlib.suppress(Exception):
        with context.open():
            client = context.acquire()
            context.release()
            raise Exception

    assert client.closed  # type: ignore
    assert context.stack == 0

    with contextlib.suppress(Exception):
        with context as client:
            raise Exception

    assert client.closed  # type: ignore
    assert context.stack == 0
