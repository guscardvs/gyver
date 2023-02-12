from typing import Any
from typing import TypeVar

# Sentinel object used to check if the __config_class__ attribute has been set on the class
SENTINEL = object()

# Generic type variable T
T = TypeVar("T")


def mark(cls: type[T]) -> type[T]:
    """
    Mark a given class as a config class.

    This function sets the attribute __config_class__ on the class,
    with the value SENTINEL. If the attribute __config_class__ already exists,
    but is not the SENTINEL, it raises a TypeError indicating that
    the attribute has an unexpected value.

    :param cls: The class to be marked as a config class.
    :type cls: type[T]
    :return: The class, marked as a config class.
    :rtype: type[T]
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

    :param obj: The object to be checked.
    :return: True if the object is marked as a config class, False otherwise.
    :rtype: bool
    """
    return getattr(obj, "__config_class__", None) is SENTINEL
