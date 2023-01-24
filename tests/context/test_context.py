import contextlib

from gyver.context import AsyncContext
from gyver.context import Context

from . import mocks


class CustomException(Exception):
    pass


def test_context_factory_returns_valid_context_on_call():
    context = Context(mocks.MockAdapter())
    with context.open():
        with context.begin() as client:
            assert context.is_active()
            assert isinstance(context, Context)

    assert client.closed
    assert context.stack == 0


async def test_async_context_factory_return_valid_async_context_on_call():
    context = AsyncContext[mocks.MockClient](mocks.MockAsyncAdapter())
    async with context.open():
        async with context.begin() as client:
            assert context.is_active()
            assert isinstance(context, AsyncContext)

    assert client.closed
    assert context._client is None
    assert context.stack == 0


def test_context_closes_correctly_when_exception_raised_on_open():
    context = Context(mocks.MockAdapter())
    with contextlib.suppress(CustomException):
        with context.open():
            client = context.client
            raise CustomException()

    assert client.closed  # type: ignore
    assert context.stack == 0


def test_context_closes_correctly_when_exception_raised_on_begin():
    context = Context(mocks.MockAdapter())
    with contextlib.suppress(CustomException):
        with context.begin() as client:
            raise CustomException()

    assert client.closed  # type: ignore
    assert context.stack == 0


async def test_asynccontext_closes_correctly_when_exception_raised_on_open():
    context = AsyncContext[mocks.MockClient](mocks.MockAsyncAdapter())
    with contextlib.suppress(CustomException):
        async with context.open():
            raise CustomException()

    assert context._client is None
    assert context.stack == 0


async def test_asynccontext_closes_correctly_when_exception_raised_on_begin():
    context = AsyncContext[mocks.MockClient](mocks.MockAsyncAdapter())
    with contextlib.suppress(CustomException):
        async with context.begin():
            raise CustomException()

    assert context._client is None
    assert context.stack == 0
