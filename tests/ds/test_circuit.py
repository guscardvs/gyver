import asyncio
from functools import partial
from unittest.mock import Mock

import pytest

from gyver.ds import CircuitBreaker, with_circuit_breaker


@pytest.fixture
def circuit_breaker():
    """Fixture providing a fresh CircuitBreaker instance for each test."""
    return CircuitBreaker()


async def test_successful_execution(circuit_breaker: CircuitBreaker):
    """Test that successful function execution works normally."""

    async def test_func():
        return "success"

    result = await circuit_breaker.execute(test_func)
    assert result == "success"
    assert not circuit_breaker.is_frozen


async def test_freezes_on_exception(circuit_breaker: CircuitBreaker):
    """Test that the circuit breaker freezes when an exception occurs."""
    # Override freeze function to be immediate for testing
    circuit_breaker.freeze_function = partial(asyncio.sleep, 0.01)

    error_mock = Mock()
    circuit_breaker.on_error = error_mock

    # Function that raises an exception
    async def failing_func():
        raise ValueError("Test error")

    # Function that doesn't raise an exception
    async def success_func():
        return "success"

    async def check():
        # Verify circuit breaker state
        assert circuit_breaker.is_frozen
        assert circuit_breaker._freeze_future is not None
        error_mock.assert_called_once()

    # First call should raise and trigger freeze
    with pytest.raises(ValueError, match="Test error"):
        await asyncio.gather(circuit_breaker.execute(failing_func), check())

    # Wait for unfreeze
    await circuit_breaker._freeze_future

    # After unfreeze, successful calls should work
    result = await circuit_breaker.execute(success_func)
    assert result == "success"
    assert not circuit_breaker.is_frozen


async def test_multiple_concurrent_executions(circuit_breaker: CircuitBreaker):
    """Test that multiple concurrent executions handle freezing correctly."""
    circuit_breaker.freeze_function = partial(asyncio.sleep, 0.1)

    # Create a failing function
    call_count = 0

    async def test_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("First call error")
        return f"Call {call_count}"

    # Start multiple tasks
    tasks = [circuit_breaker.execute(test_func) for _ in range(5)]
    results = []
    # First task should raise, others should wait and retry
    for future in asyncio.as_completed(tasks):
        try:
            result = await future
            results.append(result)
        except ValueError:
            results.append("error")

    # We should have one error and 4 successful retry calls
    assert "error" in results
    assert all(r.startswith("Call") for r in results if r != "error")
    assert call_count == 6  # 1 initial + 5 retries


async def test_decorator_functionality():
    """Test that the decorator properly wraps the function with circuit breaker logic."""
    cb = CircuitBreaker()
    cb.freeze_function = partial(asyncio.sleep, 0.01)

    execution_count = 0

    @with_circuit_breaker(cb)
    async def test_func(should_fail=False):
        nonlocal execution_count
        execution_count += 1
        if should_fail:
            raise ValueError("Decorator test error")
        return "decorator success"

    # Test successful execution
    result = await test_func()
    assert result == "decorator success"
    assert execution_count == 1

    async def check():
        await asyncio.sleep(0.01)
        assert cb.is_frozen
        assert execution_count == 2

        # Wait for unfreeze
        await cb._freeze_future

        # Test execution after unfreeze
        result = await test_func()
        assert result == "decorator success"
        assert execution_count == 4

    # Test failing execution
    for task in asyncio.as_completed((test_func(should_fail=True), check())):
        try:
            await task
        except ValueError:
            pass


async def test_custom_freeze_function(circuit_breaker: CircuitBreaker):
    """Test that a custom freeze function works correctly."""
    freeze_called = False

    async def custom_freeze():
        nonlocal freeze_called
        freeze_called = True
        await asyncio.sleep(0.01)

    circuit_breaker.freeze_function = custom_freeze

    async def failing_func():
        raise RuntimeError("Custom freeze test")

    async def check():
        assert circuit_breaker.is_frozen
        await circuit_breaker._freeze_future

        assert freeze_called
        assert not circuit_breaker.is_frozen

    # Trigger freeze
    with pytest.raises(RuntimeError):
        await asyncio.gather(circuit_breaker.execute(failing_func), check())


async def test_custom_error_handler(circuit_breaker: CircuitBreaker):
    """Test that a custom error handler is called when an exception occurs."""
    handled_exceptions = []

    def custom_handler(exc):
        handled_exceptions.append(exc)

    circuit_breaker.on_error = custom_handler
    circuit_breaker.freeze_function = partial(asyncio.sleep, 0.01)

    # Function that raises an exception
    async def failing_func():
        raise KeyError("Custom handler test")

    # Trigger error handler
    with pytest.raises(KeyError):
        await circuit_breaker.execute(failing_func)

    assert len(handled_exceptions) == 1
    assert isinstance(handled_exceptions[0], KeyError)
    assert str(handled_exceptions[0]) == "'Custom handler test'"


async def test_freeze_function_exception(circuit_breaker: CircuitBreaker):
    """Test that exceptions in the freeze function are handled properly."""

    async def failing_freeze():
        raise RuntimeError("Freeze function failed")

    circuit_breaker.freeze_function = failing_freeze

    async def test_func():
        raise ValueError("Initial error")

    async def check():
        assert circuit_breaker.is_frozen
        # Wait for the freeze future to complete (with exception)

        await circuit_breaker._freeze_future

    # First execution triggers freeze
    with pytest.raises(RuntimeError):
        await asyncio.gather(circuit_breaker.execute(test_func), check())

    assert circuit_breaker.is_frozen


async def test_reentry_during_frozen_state(circuit_breaker: CircuitBreaker):
    """Test reentry behavior when circuit is already frozen."""
    circuit_breaker.freeze_function = partial(asyncio.sleep, 0.1)

    # First trigger a freeze
    async def failing_func():
        raise ValueError("Freeze trigger")

    # Create a test function that tracks calls
    call_count = 0

    async def test_func():
        nonlocal call_count
        call_count += 1
        return f"Call {call_count}"

    async def check():
        assert circuit_breaker.is_frozen

        # Start multiple concurrent calls during frozen state
        tasks = []
        for _ in range(3):
            tasks.append(
                asyncio.create_task(circuit_breaker.execute(test_func))
            )

        # Allow the circuit breaker to unfreeze
        await asyncio.sleep(0.2)

        # All tasks should complete successfully
        results = await asyncio.gather(*tasks)

        # All calls should have occurred after unfreezing
        assert call_count == 3
        assert all(r.startswith("Call") for r in results)
        assert not circuit_breaker.is_frozen

    # Trigger initial freeze
    with pytest.raises(ValueError):
        await asyncio.gather(circuit_breaker.execute(failing_func), check())
