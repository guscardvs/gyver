import importlib
import inspect
import os
import sys
import threading
import typing
from pathlib import Path

from attrs import define

from gyver.exc import InvalidPath
from gyver.exc import MissingParams
from gyver.utils.lazy import lazyfield

StrOrPath = typing.Union[str, Path]
T = typing.TypeVar("T")
Validator = typing.Callable[[typing.Any], bool]


@define(frozen=True, slots=True)
class ModuleResolver:
    root: Path

    @staticmethod
    def convert_path(path: Path):
        return Path.as_posix(path)

    @lazyfield
    def _root_converted(self):
        return self.convert_path(self.root)

    def from_path(self, path: Path):
        target_str = self.convert_path(path)
        return (
            target_str.replace(self._root_converted, self.root.name)
            .removesuffix(".py")
            .replace("/", ".")
        )


@define(frozen=True, slots=True)
class ModuleIterator:
    modpath: Path
    resolver: ModuleResolver

    def __iter__(self):
        mod = importlib.import_module(self.resolver.from_path(self.modpath))
        yield from inspect.getmembers(mod)


@define(frozen=True)
class _Finder:
    validator: Validator
    root: Path
    look_on: typing.Optional[Path] = None
    exclude: typing.Sequence[StrOrPath] = ()

    def find(self):
        if self.target_path.is_dir():
            self._iterdir(self.target_path)
        else:
            self._itermod(self.target_path)

    @classmethod
    def instance_of(
        cls,
        class_: type[T],
        root: Path,
        look_on: typing.Optional[Path] = None,
        exclude: typing.Sequence[StrOrPath] = (),
    ) -> dict[str, T]:
        finder = cls(instance_validator(class_), root, look_on, exclude)
        finder.find()
        return finder.output

    @classmethod
    def child_of(
        cls,
        class_: type[T],
        root: Path,
        look_on: typing.Optional[Path] = None,
        exclude: typing.Sequence[StrOrPath] = (),
    ) -> dict[str, T]:
        finder = cls(class_validator(class_), root, look_on, exclude)
        finder.find()
        return finder.output

    def __post_init__(self):
        if not self.root.exists():
            raise InvalidPath(
                f"root must be a valid path, received {self.root}"
            )

    def _should_look(self, path: Path):
        str_exclude = tuple(
            item for item in self.exclude if isinstance(item, str)
        )
        path_exclude = tuple(
            item for item in self.exclude if isinstance(item, Path)
        )
        return (
            path.name not in str_exclude
            and path not in path_exclude
            and (not path.is_file() or path.name.endswith(".py"))
        )

    @lazyfield
    def target_path(self):
        return self.look_on or self.root

    @lazyfield
    def output(self):
        return {}

    @lazyfield
    def resolver(self):
        return ModuleResolver(self.root)

    def _iterdir(self, path: Path):
        for item in path.iterdir():
            if not self._should_look(item):
                continue
            if item.is_dir():
                self._iterdir(path)
            else:
                self._itermod(path)

    def _itermod(self, path: Path):
        for name, obj in ModuleIterator(path, self.resolver):
            if self.validator(obj):
                self.output[name] = obj


def class_validator(*types: type):
    if not types:
        raise MissingParams("Missing types in class_validator paramaters")

    def validator(obj: typing.Any):
        return (
            issubclass(obj, types) and obj not in types
            if inspect.isclass(obj)
            else False
        )

    return validator


def instance_validator(*types: type):
    if not types:
        raise MissingParams("Missing types in instance_validator paramaters")

    def validator(obj: typing.Any):
        return isinstance(obj, types)

    return validator


class FinderFactory:
    def __init__(self) -> None:
        self.root: typing.Optional[Path] = None
        self._validators = []
        self._lock = threading.Lock()
        self._exclude = []

    def from_path(self, path: Path):
        self.root = path
        return self

    def from_cwd(self):
        return self.from_path(Path.cwd())

    def from_project(self):
        return self.from_path(
            Path(os.path.dirname(sys.modules["__main__"].__file__)),  # type: ignore
        )

    def _validator(self, obj: typing.Any) -> bool:
        return all(validator(obj) for validator in self._validators)

    def add_validator(self, validator: Validator):
        with self._lock:
            self._validators.append(validator)
        return self

    def child_of(self, *types: type):
        return self.add_validator(class_validator(*types))

    def instance_of(self, *types: type):
        return self.add_validator(instance_validator(*types))

    def exclude(self, *paths: StrOrPath):
        self._exclude.extend(paths)
        return self

    def exclude_default(self):
        return self.exclude("__init__.py", "__pycache__")

    def find(
        self,
        look_on: typing.Optional[Path] = None,
    ):
        with self._lock:
            if self.root is None:
                self.from_project()
                assert self.root is not None
            finder = _Finder(
                self._validator,
                self.root,
                look_on,
            )
            finder.find()
            return finder.output


default_factory = FinderFactory()
