import sys
from itertools import chain
from collections.abc import Sequence


class GyverError(Exception):
    """Base exception for all exceptions raised by the Gyver library."""


class InvalidCast(GyverError):
    """Raised when an error occurs during a casting operation in configuration."""


class MissingName(GyverError, KeyError):
    """Raised when a required name is missing in the provided environment configuration."""


class InvalidField(GyverError, KeyError):
    """Raised when an unexpected result is encountered during a field lookup on a mapping."""


class CacheMiss(GyverError, KeyError):
    """Raised when a cache lookup returns None or raises an error."""


class MissingParams(GyverError, NotImplementedError):
    """Raised when a function expecting *args parameters receives none."""


class InvalidPath(GyverError, ValueError):
    """Raised when an invalid file or directory path is encountered."""


class InvalidParamType(GyverError, TypeError):
    """Raised when a parameter's type is not as expected."""


class InvalidParamValue(GyverError, ValueError):
    """Raised when a parameter's value is unexpected."""


if sys.version_info < (3, 11):

    class ErrorGroup(GyverError):
        """
        Exception that groups multiple sub-exceptions.

        This exception is used to encapsulate and present multiple related exceptions as a group.
        It provides a way to handle multiple errors together in a unified manner.
        """

        exceptions: tuple[Exception, ...]

        def __init__(self, message: str, exceptions: Sequence[Exception]) -> None:
            self.message = message
            self.exceptions = tuple(exceptions)
            args = list(chain(item.args for item in exceptions))
            super().__init__(self.message, *args)

        def __str__(self) -> str:
            suffix = "" if len(self.exceptions) == 1 else "s"
            return f"{self.message} ({len(self.exceptions)} sub-exception{suffix})"

        def __repr__(self) -> str:
            return f"{self.__class__.__name__}({self.message!r}, {self.exceptions!r})"

else:

    class ErrorGroup(GyverError, ExceptionGroup):  # noqa: F821
        """
        Exception that groups multiple sub-exceptions.

        This exception is used to encapsulate and present multiple related exceptions as a group.
        It provides a way to handle multiple errors together in a unified manner.
        """


class FailedFileOperation(GyverError):
    """Raised when an error occurs during an interaction with a file."""


class MergeConflict(GyverError):
    """Raised when a merge conflict is detected, e.g., during the merge_dicts operation."""
