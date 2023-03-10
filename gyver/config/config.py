import os
from os import environ
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Iterator
from typing import MutableMapping
from typing import TypeVar
from typing import Union
from typing import overload

from gyver.exc import InvalidCast
from gyver.exc import MissingName
from gyver.utils.exc import panic
from gyver.attrs import define, info

from gyver.utils.lazy import lazyfield

T = TypeVar("T")


@define
class EnvMapping(MutableMapping[str, str]):
    mapping: MutableMapping[str, str] = environ
    already_read: set[str] = info(default_factory=set)

    def __getitem__(self, name: str):
        val = self.mapping[name]
        self.already_read.add(name)
        return val

    def __setitem__(self, name: str, value: str):
        if name in self.already_read:
            raise panic(
                KeyError, f"{name} already read, cannot change its value"
            )
        self.mapping[name] = value

    def __delitem__(self, name: str) -> None:
        if name in self.already_read:
            raise panic(KeyError, f"{name} already read, cannot delete")
        del self.mapping[name]

    def __iter__(self) -> Iterator[str]:
        yield from self.mapping

    def __len__(self) -> int:
        return len(self.mapping)


default_mapping = EnvMapping()


class MISSING:
    pass


def _default_cast(a: Any):
    return a


@define
class Config:
    env_file: Union[str, Path, None] = None
    mapping: EnvMapping = default_mapping

    def __post_init__(self):
        if self.env_file and os.path.isfile(self.env_file):
            self.file_values.update(dict(self._read_file(self.env_file)))

    @lazyfield
    def file_values(self):
        return {}

    def _read_file(self, env_file: Union[str, Path]):
        with open(env_file) as buf:
            for line in buf:
                if line.startswith("#"):
                    continue
                name, value = line.split("=", 1)
                yield name.strip(), value.strip()

    def _cast(self, name: str, val: Any, cast: Callable) -> Any:
        try:
            val = cast(val)
        except Exception as e:
            raise panic(
                InvalidCast, f"{name} received an invalid value {val}"
            ) from e
        else:
            return val

    def _get_val(
        self, name: str, default: Union[Any, type[MISSING]] = MISSING
    ) -> Union[Any, type[MISSING]]:
        return self.mapping.get(name, self.file_values.get(name, default))

    def get(
        self,
        name: str,
        cast: Callable = _default_cast,
        default: Union[Any, type[MISSING]] = MISSING,
    ) -> Any:
        val = self._get_val(name, default)
        if val is MISSING:
            raise panic(
                MissingName, f"{name} not found and no default was given"
            )
        return self._cast(name, val, cast)

    @overload
    def __call__(
        self,
        name: str,
        cast: Union[Callable[[Any], T], type[T]] = _default_cast,
        default: type[MISSING] = MISSING,
    ) -> T:
        ...

    @overload
    def __call__(
        self,
        name: str,
        cast: Union[Callable[[Any], T], type[T]] = _default_cast,
        default: T = ...,
    ) -> T:
        ...

    def __call__(
        self,
        name: str,
        cast: Union[Callable[[Any], T], type[T]] = _default_cast,
        default: Union[T, type[MISSING]] = MISSING,
    ) -> T:
        return self.get(name, cast, default)
