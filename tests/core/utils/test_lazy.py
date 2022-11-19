from dataclasses import FrozenInstanceError
from dataclasses import dataclass
from typing import Callable
from typing import Generic
from typing import TypeVar
from unittest.mock import Mock

import pytest

from gyver import utils

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
