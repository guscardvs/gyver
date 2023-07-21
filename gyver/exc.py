import sys
from itertools import chain
from typing import Sequence


class GyverError(Exception):
    """Base exception for all gyver exceptions"""


class InvalidCast(GyverError):
    """Exception raised for config when
    cast callable raises an error"""


class MissingName(GyverError, KeyError):
    """Exception raised for config when
    name is not found in given environ"""


class InvalidField(GyverError, KeyError):
    """Exception raised when field lookup
    returned an unexpected result on mapping"""


class CacheMiss(GyverError, KeyError):
    """Exception raised when cache lookup
    returns None or raises error"""


class QueueNotFound(InvalidField):
    """Exception raised when queue name provider
    does not exist on given credentials"""


class MissingParams(GyverError, NotImplementedError):
    """Exception raised when no params where passed in a
    *args function
    """


class InvalidPath(GyverError, ValueError):
    """Equivalent to FileNotFound but also for directories"""


class InvalidParamType(GyverError, TypeError):
    """Exception raised when parameter received
    is not of the type excpected"""


class InvalidParamValue(GyverError, ValueError):
    """Exception raised when parameter received
    has an unexpected value"""


if sys.version_info < (3, 11):

    class ErrorGroup(GyverError):
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

    class ErrorGroup(GyverError, ExceptionGroup): # noqa: F821
        pass


class FailedFileOperation(GyverError):
    """Exception raised when an error happened while interacting with a file"""


class MergeConflict(GyverError):
    """Exception raised when merge_dicts(strict=True) finds a conflict"""
