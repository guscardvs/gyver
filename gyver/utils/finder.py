import importlib
import inspect
import pathlib
import typing
from dataclasses import dataclass

from gyver.exc import GyverError

from .lazy import lazyfield

T = typing.TypeVar("T")

Validator = typing.Callable[[typing.Any], bool]
StrOrPath = typing.Union[str, pathlib.Path]
_convert_path = pathlib.Path.as_posix


class InvalidPath(GyverError, ValueError):
    pass


@dataclass(frozen=True)
class Finder:
    """Finder can be used to search for and import specific entities
    (defined by a user-provided validator function) from a codebase."""

    validator: Validator
    root: pathlib.Path
    look_on: typing.Optional[pathlib.Path] = None
    exclude: typing.Sequence[StrOrPath] = ()

    def __post_init__(self):
        if not self.root.exists():
            raise InvalidPath(f"root must be a valid path, received {self.root}")

    @property
    def _look_on(self):
        return self.look_on or self.root

    @lazyfield
    def _exclude(self):
        return *self.exclude, "__init__.py", "__pycache__"

    @lazyfield
    def output(self) -> dict[str, typing.Any]:
        return {}

    def find(self):
        if self._look_on.is_dir():
            self._iterate_folder(self._look_on)
        else:
            self._iterate_file_contents(self._look_on)

    def _make_module_name(self, path: pathlib.Path):
        target_str = _convert_path(path)
        return (
            target_str.replace(_convert_path(self.root), self.root.name)
            .removesuffix(".py")
            .replace("/", ".")
        )

    def _should_look(self, path: pathlib.Path):
        str_exclude = tuple(item for item in self._exclude if isinstance(item, str))
        path_exclude = tuple(
            item for item in self._exclude if isinstance(item, pathlib.Path)
        )
        return (
            path.name not in str_exclude
            and path not in path_exclude
            and (not path.is_file() or path.name.endswith(".py"))
        )

    def _iterate_folder(self, path: pathlib.Path):
        for item in path.iterdir():
            if not self._should_look(item):
                continue
            if item.is_dir():
                self._iterate_folder(item)
            else:
                self._iterate_file_contents(item)

    def _iterate_file_contents(self, path: pathlib.Path):
        mod = importlib.import_module(self._make_module_name(path))
        for name, obj in inspect.getmembers(mod):
            if self.validator(obj):
                self.output[name] = obj


class MissingParams(GyverError, NotImplementedError):
    pass


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
