from typing import TypeVar

T = TypeVar("T", bound=Exception)


def panic(exc: type[T], message: str, *args) -> T:
    """
    Create an instance of the specified exception class with a modified error message.

    This function creates an exception instance by calling the constructor of the
    specified exception class with the modified error message and any additional
    arguments provided.

    :param exc: The exception class to instantiate.
    :param message: The error message for the exception.
    :param args: Additional arguments to pass to the exception constructor.
    :return: An instance of the specified exception class.

    Example:
    >>> class CustomError(Exception):
    ...     pass
    ...
    >>> error = panic(CustomError, "Something went wrong", "additional_info")
    >>> isinstance(error, CustomError)
    True
    >>> str(error)
    'Something went wrong! additional_info'
    """
    return exc(message.removesuffix("!") + "!", *args)
