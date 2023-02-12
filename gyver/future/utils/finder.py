import importlib
import inspect
import os
import pathlib
import sys
import threading
import typing

from gyver.exc import InvalidPath
from gyver.exc import MissingParams
from gyver.utils import frozen
from gyver.utils import lazyfield

PathConverter = typing.Callable[[pathlib.Path], str]
StrOrPath = typing.Union[str, pathlib.Path]
T = typing.TypeVar("T")
Validator = typing.Callable[[typing.Any], bool]


def make_modulename_resolver(
    root: pathlib.Path, path_converter: PathConverter = pathlib.Path.as_posix
) -> PathConverter:
    root_str = path_converter(root)

    def module_resolveer(path: pathlib.Path) -> str:
        target_str = path_converter(path)
        return (
            target_str.replace(root_str, root.name)
            .removesuffix(".py")
            .replace("/", ".")
        )

    return module_resolveer


def iterate_module(modpath: pathlib.Path, resolver: PathConverter):
    mod = importlib.import_module(resolver(modpath))
    yield from inspect.getmembers(mod)


@frozen
class _Finder:
    validator: Validator
    root: pathlib.Path
    look_on: typing.Optional[pathlib.Path] = None
    exclude: typing.Sequence[StrOrPath] = ()

    def __iter__(self):
        return self._iterdir(self.root)

    def find(self):
        return self.output

    @lazyfield
    def output(self):
        return dict(self)

    def __attrs_post_init__(self):
        if not self.root.exists():
            raise InvalidPath(
                f"root must be a valid path, received {self.root}"
            )

    def _should_look(self, path: pathlib.Path):
        str_exclude = tuple(
            item for item in self.exclude if isinstance(item, str)
        )
        path_exclude = tuple(
            item for item in self.exclude if isinstance(item, pathlib.Path)
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
    def resolver(self) -> PathConverter:
        return make_modulename_resolver(self.root)

    def _itermod(self, path: pathlib.Path):
        yield from (
            (name, obj)
            for name, obj in iterate_module(path, self.resolver)
            if self.validator(obj)
        )

    def _iterdir(
        self, path: pathlib.Path
    ) -> typing.Generator[tuple[str, typing.Any], None, None]:
        for item in path.iterdir():
            if not self._should_look(item):
                continue
            if item.is_dir():
                yield from self._iterdir(item)
            else:
                yield from self._itermod(item)


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


class FinderBuilder:
    def __init__(self) -> None:
        self.root: typing.Optional[pathlib.Path] = None
        self._validators = []
        self._lock = threading.Lock()
        self._exclude = []

    def reset(self):
        with self._lock:
            self.root = None
            self._validators = []
            self._exclude = []

    def from_path(self, path: pathlib.Path):
        if not path.exists():
            raise InvalidPath(f"root must be a valid path, received {path}")
        self.root = path
        return self

    def from_cwd(self):
        return self.from_path(pathlib.Path.cwd())

    def from_project(self):
        """
        Finds the root path of the project based on the file where this
        method was called. It works by checking the `sys.path` to find
        the longest path that contains the path to the file.
        This path is considered to be the root path of the project.

        Returns:
            The `FinderBuilder` object with the project root path set.
        """
        frame_stack: list[inspect.FrameInfo] = inspect.stack()

        frame_info: inspect.FrameInfo = frame_stack[1]

        if frame_info.filename == __file__:
            frame_info = next(
                frame for frame in frame_stack if frame.filename != __file__
            )

        caller_path: str = frame_info.filename
        caller_absolute_path: str = os.path.abspath(caller_path)

        caller_root_path = next(
            iter(
                sorted(
                    (p for p in sys.path if p in caller_absolute_path),
                    key=lambda p: len(p),
                )
            )
        )

        if not os.path.isabs(caller_path):
            caller_module_name: str = pathlib.Path(caller_path).name
            project_related_folders: str = caller_path.replace(
                os.sep + caller_module_name, ""
            )

            caller_root_path = caller_root_path.replace(
                project_related_folders, ""
            )

        return self.from_path(pathlib.Path(caller_root_path))

    def from_package(self, stack_position: int = 1):
        """
        Finds the root path of the package that called the method and sets it as the
        base path for the finder.

        Parameters:
        stack_position (int, optional): The position in the stack trace of the calling
        function. The default is 1, which is the immediate caller.

        Returns:
        FinderBuilder: The FinderBuilder object, with the base path set to the
        root path of the calling package.
        """
        frame_stack = inspect.stack()

        frame_info = frame_stack[stack_position]

        if frame_info.filename == __file__:
            frame_info = next(
                frame for frame in frame_stack if frame.filename != __file__
            )

        package: str = frame_info.frame.f_globals["__name__"]
        steps_to_package = len(package.split("."))
        caller_root_path = pathlib.Path(package.replace(".", "/")).resolve()
        for _ in range(steps_to_package - 1):
            caller_root_path = caller_root_path.parent
        return self.from_path(pathlib.Path(caller_root_path))

    def _make_validator(self):
        validators = [*self._validators]

        def _validator(obj: typing.Any):
            return all(validator(obj) for validator in validators)

        return _validator

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

    def build(
        self,
        look_on: typing.Optional[pathlib.Path] = None,
    ) -> _Finder:
        with self._lock:
            if self.root is None:
                self.from_package()
            finder = _Finder(
                self._make_validator(),
                typing.cast(pathlib.Path, self.root),
                look_on,
            )
        self.reset()
        return finder

    def find(
        self,
        look_on: typing.Optional[pathlib.Path] = None,
    ):
        if self.root is None:
            self.from_project()
            assert self.root is not None
        return self.build(look_on).find()


builder = FinderBuilder()
