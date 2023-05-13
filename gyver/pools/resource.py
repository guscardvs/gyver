from time import time
from typing import Any
from typing import Generic
from typing import TypeVar

from gyver.attrs import define
from gyver.attrs import mutable

from gyver.exc import InvalidParamType

T = TypeVar("T")


STARTTIME_ATTR = "_gyver_starttime_"


@mutable
class ResourceProxy:
    _target: Any
    _gyver_starttime_: float

    def __init__(self, target: Any, starttime: float):
        object.__setattr__(self, "_target", target)
        object.__setattr__(self, "_gyver_starttime_", starttime)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._target, name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_gyver_starttime_":
            super().__setattr__(name, value)
        else:
            setattr(self._target, name, value)

    def __delattr__(self, name: str) -> None:
        delattr(self._target, name)

    @classmethod
    def as_any(cls, target: Any, starttime: float) -> Any:
        return cls(target, starttime)


@define
class Resource(Generic[T]):
    resource: T

    @classmethod
    def from_now(cls, resource: T) -> "Resource[T]":
        """
        Create a `Resource` object with the current timestamp as the `last_usage` value.

        :param resource: The underlying resource.
        :return: The `Resource` object.
        """
        current_ts = time()
        return cls(ResourceProxy.as_any(resource, current_ts))

    @classmethod
    def from_resource(cls, resource: T) -> "Resource[T]":
        """
        Create a `Resource` object from an existing resource.

        :param resource: The underlying resource.
        :return: The `Resource` object.
        :raises: InvalidParamType if the resource was not initialized correctly.
        """
        if not hasattr(resource, STARTTIME_ATTR):
            raise InvalidParamType(
                "Resource was not initialized correctly", resource
            ) from None
        return cls(resource)

    @property
    def last_usage(self) -> float:
        return getattr(self.resource, STARTTIME_ATTR)

    def get(self) -> T:
        """
        Get the underlying resource.

        :return: The underlying resource.
        """
        return self.resource
