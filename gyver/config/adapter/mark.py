from typing import Any, TypeVar

import typing_extensions

from gyver.attrs import define
from gyver.attrs.field import FieldInfo, info

# Sentinel object used to check if the __config_class__ attribute
# has been set on the class
SENTINEL = object()

# Generic type variable T
T = TypeVar("T")


def mark(cls: type[T]) -> type[T]:
    """
    Mark a given class as a config class.
    If the attribute __config_class__ already exists,
    but is not the SENTINEL, it raises a TypeError indicating that
    the attribute has an unexpected value.
    It is used by the [resolve_confignames][gyver.config.AdapterConfigFactory] to
    differentiate config classes

    Args:
        cls (type[T]): The class to be marked as a config class.

    Returns:
        type[T]: The class, marked as a config class.
    """
    if getattr(cls, "__config_class__", SENTINEL) is not SENTINEL:
        raise TypeError("Variable __config_class__ has an unexpected value")
    setattr(cls, "__config_class__", SENTINEL)
    return cls


def is_config(obj: Any) -> bool:
    """
    Check if an object is marked as a config class.

    This function checks if the attribute __config_class__
    exists on the object and if it is equal to SENTINEL.

    Args:
        obj (Any): The object to be checked.

    Returns:
        bool: True if the object is marked as a config class, False otherwise.
    """
    return getattr(obj, "__config_class__", None) is SENTINEL


@typing_extensions.dataclass_transform(
    order_default=True,
    frozen_default=True,
    kw_only_default=False,
    field_specifiers=(FieldInfo, info),
)
def as_config(cls: type[T]) -> type[T]:
    """
    Transform a class into a config class.

    This function applies the @define decorator from gyver.attrs and also marks
    the class as a config_class

    Args:
        cls (type[T]): The class to be transformed into a config class.

    Returns:
        type[T]: The transformed class, marked as a config class.
    """
    return mark(define(cls))
