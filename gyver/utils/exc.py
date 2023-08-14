from typing import TypeVar

T = TypeVar("T", bound=Exception)


def panic(exc: type[T], message: str, *args) -> T:
    """
    Create an instance of the specified exception class with a modified error message.

    This function creates an exception instance by calling the constructor of the
    specified exception class with the modified error message and any additional
    arguments provided.

    Args:
        exc (type[T]): The exception class to instantiate.
        message (str): The error message for the exception.
        *args (Any): Additional arguments to pass to the exception constructor.

    Returns:
        T: An instance of the specified exception class.

    Examples:
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
