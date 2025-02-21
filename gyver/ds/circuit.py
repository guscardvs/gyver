import asyncio
import logging
from collections.abc import Callable, Coroutine
from functools import partial, wraps
from typing import Any, ParamSpec, TypeVar

from gyver.attrs import mutable, private

T = TypeVar("T")
P = ParamSpec("P")


def _default_on_err(exc: Exception):
    """Logs an exception that occurs during CircuitBreaker execution.

    Args:
        exc (Exception): The exception that was raised.
    """
    logging.exception("Failed execution during CircuitBreaker execution")


DEFAULT_DELAY = 5  # seconds


@mutable
class CircuitBreaker:
    """Implements a circuit breaker pattern for handling failures in async operations.

    Attributes:
        freeze_function (Callable[[], Coroutine]): The function to execute during the frozen state.
        on_error (Callable[[Exception], None]): The callback to execute when an error occurs.
        _lock (asyncio.Lock): Lock to ensure thread safety when modifying state.
        _frozen (bool): Indicates whether the circuit breaker is currently frozen.
        _freeze_future (asyncio.Future | None): Future that represents when the circuit breaker will unfreeze.
    """

    freeze_function: Callable[[], Coroutine] = partial(
        asyncio.sleep, DEFAULT_DELAY
    )
    on_error: Callable[[Exception], None] = _default_on_err
    _lock: asyncio.Lock = private(initial_factory=asyncio.Lock)
    _frozen: bool = private(initial=False)
    _freeze_future: asyncio.Future | None = private(initial=None)

    async def execute(
        self,
        func: Callable[P, Coroutine[Any, Any, T]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T:
        """Executes the provided function with circuit breaker logic.

        If the circuit breaker is frozen, waits for it to unfreeze before retrying execution.
        If an exception occurs, triggers the freezing mechanism.

        Args:
            func (Callable[P, Coroutine[Any, Any, T]]): The async function to execute.
            *args (P.args): Positional arguments to pass to the function.
            **kwargs (P.kwargs): Keyword arguments to pass to the function.

        Returns:
            T: The result of the function execution.

        Raises:
            Any exception that occurs during execution after the circuit breaker is unfrozen.
        """
        if not self._frozen:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                self.on_error(e)
                async with self._lock:
                    if not self._frozen:
                        await self._freeze(e)

        if self._freeze_future is not None:
            await self._freeze_future

        return await func(*args, **kwargs)

    @property
    def is_frozen(self):
        return self._frozen

    async def _freeze(self, error: Exception) -> None:
        """Freezes the circuit breaker for a predefined duration.

        Args:
            error (Exception): The exception that caused the freeze.
        """
        self._frozen = True
        loop = asyncio.get_running_loop()
        frozen_future = loop.create_future()
        self._freeze_future = frozen_future

        async def unfreeze():
            try:
                await self.freeze_function()
                self._frozen = False
                frozen_future.set_result(None)
            except Exception as e:
                frozen_future.set_exception(e)

        asyncio.create_task(unfreeze())


def with_circuit_breaker(circuit_breaker: CircuitBreaker):
    """Decorator that applies a CircuitBreaker to an async function.

    Args:
        circuit_breaker (CircuitBreaker): The circuit breaker instance to use.

    Returns:
        Callable[P, Coroutine[Any, Any, T]]: A wrapped function that applies circuit breaker logic.
    """

    def decorator(
        func: Callable[P, Coroutine[Any, Any, T]],
    ) -> Callable[P, Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            """Wrapper function that executes the given function within the circuit breaker."""
            return await circuit_breaker.execute(func, *args, **kwargs)

        return wrapper

    return decorator
