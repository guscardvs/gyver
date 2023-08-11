import functools
import warnings
from collections import deque
from itertools import chain
from typing import Callable
from typing import Literal
from typing import TypeVar
from typing import cast

from gyver.attrs import define
from typing_extensions import ParamSpec

from gyver.exc import MergeConflict

P = ParamSpec("P")
T = TypeVar("T")


def cache(f: Callable[P, T]) -> Callable[P, T]:
    """
    Cache the result of a function.

    :param f: The function to be cached.
    :return: The cached version of the function.
    """
    return cast(Callable[P, T], functools.cache(f))


def deprecated(func: Callable[P, T]) -> Callable[P, T]:
    """
    Mark a function as deprecated and issue a warning when it's used.

    :param func: The function to be marked as deprecated.
    :return: A wrapped version of the function that issues a warning on use.
    """
    @functools.wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        if not hasattr(func, "__warn_deprecated__"):
            warnings.warn(
                f"{func.__qualname__} is "
                "deprecated and can be removed without notice",
                DeprecationWarning,
            )
            func.__warn_deprecated__ = True
        return func(*args, **kwargs)

    return inner


frozen = deprecated(define)


class DeprecatedClass:
    """
    A class to mark as deprecated.

    This class issues a deprecation warning when instantiated.
    """
    __warn_deprecated__ = False

    def __init__(self) -> None:
        if not type(self).__warn_deprecated__:
            warnings.warn(
                f"{'.'.join((type(self).__module__, type(self).__name__))} is "
                "deprecated and can be removed without notice",
                DeprecationWarning,
            )
            type(self).__warn_deprecated__ = True


def merge_dicts(
    left: dict,
    right: dict,
    on_conflict: Literal["strict", "left", "right"],
    merge_sequences: bool = True,
) -> dict:
    """
    Merge two dictionaries with customizable conflict resolution strategy.

    :param left: The left dictionary to merge.
    :type left: dict
    :param right: The right dictionary to merge.
    :type right: dict
    :param on_conflict: The conflict resolution strategy to use.
        - 'strict': Raise a MergeConflict exception if conflicts occur.
        - 'left': Prioritize the values from the left dictionary in case of conflicts.
        - 'right': Prioritize the values from the right dictionary in case of conflicts.

    :type on_conflict: Literal["strict", "left", "right"]
    :param merge_sequences: Indicates whether to merge sequences (lists, sets, tuples) or skip them.
        If True, sequences will be merged based on the conflict resolution strategy.
        If False, sequences will be skipped, and the value from the chosen (defaults to left on strict)
            dictionary will be used.
    :type merge_sequences: bool, optional
    :return: The merged dictionary.
    :rtype: dict

    :raises MergeConflict: If conflicts occur and the conflict resolution strategy is set to 'strict'.
    """

    output = {key: value for key, value in left.items() if key not in right}

    stack = deque([(left, right, output)])

    while stack:
        left_curr, right_curr, output_curr = stack.pop()

        for key, value in right_curr.items():
            if key not in left_curr:
                output_curr[key] = value
            elif isinstance(value, (list, set, tuple)) and merge_sequences:
                left_val = left_curr[key]
                if isinstance(left_val, (list, set, tuple)):
                    type_ = type(value) if on_conflict == "right" else type(left_val)
                    output_curr[key] = type_(chain(left_val, value))
            elif isinstance(value, dict):
                if isinstance(left_curr[key], dict):
                    output_curr[key] = {
                        lkey: lvalue
                        for lkey, lvalue in left_curr[key].items()
                        if lkey not in value
                    }
                    stack.append((left_curr[key], value, output_curr[key]))
            elif on_conflict not in ("left", "right"):
                raise MergeConflict(
                    "Conflict found when trying to merge dicts",
                    key,
                    value,
                    left_curr[key],
                )
            elif on_conflict == "left":
                output_curr[key] = left_curr[key]
            else:
                output_curr[key] = value

    return output
