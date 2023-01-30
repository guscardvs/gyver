import warnings

from gyver.utils.helpers import deprecated


def test_deprecated_decorator():
    # Helper function to capture warnings
    def capture_warnings(func, *args, **kwargs):
        with warnings.catch_warnings(record=True) as warns:
            warnings.simplefilter("always")
            result = func(*args, **kwargs)
            return result, warns

    @deprecated
    def deprecated_function():
        return "Hello World"

    result, warns = capture_warnings(deprecated_function)
    assert result == "Hello World"
    assert len(warns) == 1
    assert issubclass(warns[-1].category, DeprecationWarning)
    assert "deprecated_function is deprecated" in str(warns[-1].message)

    # Ensure the warning is only raised once
    result, warns = capture_warnings(deprecated_function)
    assert result == "Hello World"
    assert len(warns) == 0
