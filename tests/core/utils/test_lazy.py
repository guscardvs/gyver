import asyncio
from dataclasses import FrozenInstanceError
from dataclasses import dataclass
from typing import Any, Callable, Coroutine
from typing import Generic
from typing import TypeVar
from unittest.mock import Mock

import pytest

from gyver import utils
from gyver.attrs import mutable

T = TypeVar("T")


class Fake(Generic[T]):
    def __init__(self, slow_func: Callable[[], T]) -> None:
        self._slow_func = slow_func

    @utils.lazyfield
    def test(self) -> T:
        return self._slow_func()


@dataclass(init=False, frozen=True)
class FrozenFake(Fake[T]):
    def __init__(self, slow_func: Callable[[], T]) -> None:
        object.__setattr__(self, "_slow_func", slow_func)


class AsyncFake(Generic[T]):
    def __init__(
        self, slow_func: Callable[[], Coroutine[Any, Any, T]]
    ) -> None:
        self._slow_func = slow_func

    @utils.asynclazyfield
    async def test(self) -> T:
        return await self._slow_func()


@dataclass(init=False, frozen=True)
class AsyncFrozenFake(AsyncFake[T]):
    def __init__(self, slow_func: Callable[[], T]) -> None:
        object.__setattr__(self, "_slow_func", slow_func)


def test_lazy_field_return_value_correctly():
    run_count = 0

    def slow_func():
        nonlocal run_count
        run_count += 1
        return "hello"

    fake = Fake(slow_func)
    assert fake.test == "hello"
    assert run_count == 1


def test_lazy_field_updates_value_on_set():
    mock = Mock()
    fake = Fake(mock)
    fake.test = "world"

    assert fake.test == "world"
    assert not mock.called


def test_lazy_field_resets_value_on_set():
    mock = Mock()
    mock.return_value = "hello"
    fake = Fake(mock)
    fake.test = "world"

    del fake.test

    assert fake.test == "hello"
    assert mock.called_once()


def test_lazy_field_respects_frozen_in_class():
    mock = Mock()
    mock.return_value = "hello"
    fake = FrozenFake(mock)

    assert fake.test == "hello"
    with pytest.raises(FrozenInstanceError):
        fake.test = "world"
    with pytest.raises(FrozenInstanceError):
        del fake.test


### Async


@mutable
class MockFuture:
    return_value: str = ""
    awaitable: int = 0

    async def __call__(self):
        self.awaitable += 1
        return self.return_value


async def test_async_lazy_field_return_value_correctly():
    future = MockFuture(return_value="hello")

    fake = AsyncFake(future)
    assert await fake.test() == "hello"
    assert future.awaitable == 1


async def test_async_lazy_field_updates_value_on_set():
    mock = MockFuture()
    fake = AsyncFake(mock)
    utils.setlazy(fake, "test", "world")

    assert await fake.test() == "world"
    assert not mock.awaitable


async def test_async_lazy_field_resets_value_on_set():
    mock = MockFuture(return_value="hello")

    fake = AsyncFake(mock)
    utils.setlazy(fake, "test", "world")

    utils.dellazy(fake, "test")

    assert await fake.test() == "hello"
    assert mock.awaitable == 1


async def test_async_lazy_field_respects_frozen_in_class():
    mock = MockFuture(return_value="hello")
    fake = AsyncFrozenFake(mock)

    assert await fake.test() == "hello"
    with pytest.raises(FrozenInstanceError):
        utils.setlazy(fake, "test", "world")
    with pytest.raises(FrozenInstanceError):
        utils.dellazy(fake, "test")
