import importlib
import inspect
import os
import pathlib
import sys
import threading
import typing
from typing_extensions import Self
from gyver.attrs import define

from gyver.exc import InvalidPath
from gyver.exc import MissingParams
from gyver.utils.lazy import lazyfield

PathConverter = typing.Callable[[pathlib.Path], str]
StrOrPath = typing.Union[str, pathlib.Path]
T = typing.TypeVar("T")
Validator = typing.Callable[[typing.Any], bool]


def make_modulename_resolver(
    root: pathlib.Path, path_converter: PathConverter = pathlib.Path.as_posix
) -> PathConverter:
    """
    Create a module name resolver based on a root path.

    Args:
        root (pathlib.Path): The root path to resolve from.
        path_converter (PathConverter, optional): A path converter function (default: pathlib.Path.as_posix).

    Returns:
        PathConverter: A callable that resolves a path into a module name.
    """
    root_str = path_converter(root)

    def module_resolver(path: pathlib.Path) -> str:
        target_str = path_converter(path)
        return (
            target_str.replace(root_str, root.name)
            .removesuffix(".py")
            .replace("/", ".")
        )

    return module_resolver


def iterate_module(
    modpath: pathlib.Path, resolver: PathConverter
) -> typing.Generator[tuple[str, typing.Any], None, None]:
    """
    Iterate through a module using a resolver to map paths to module names.

    Args:
        modpath (pathlib.Path): The path to the module.
        resolver (PathConverter): A path converter to map paths to module names.

    Yields:
        tuple[str, Any]: A tuple containing the name and object of each item in the module.
    """
    mod = importlib.import_module(resolver(modpath))
    yield from inspect.getmembers(mod)


@define
class _Finder:
    """
    Finder class to locate and validate objects in a given directory structure.

    Attributes:
        validator (Validator): The validation function for objects.
        root (pathlib.Path): The root path to start searching.
        look_on (Optional[pathlib.Path]): The path to focus the search on (default: None).
        exclude (Sequence[StrOrPath]): Paths to exclude from search (default: []).
    """

    validator: Validator
    root: pathlib.Path
    look_on: typing.Optional[pathlib.Path] = None
    exclude: typing.Sequence[StrOrPath] = ()

    def __iter__(self):
        """
        Create an iterator for the finder.
        """
        return self._iterdir(self.root)

    def find(self):
        """
        Find and return the output dictionary containing the located objects.

        Returns:
            dict: The dictionary containing the located objects.
        """
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
        """
        Determine whether the given path should be explored or not.

        Args:
            path (pathlib.Path): The path to evaluate.

        Returns:
            bool: True if the path should be explored, False otherwise.
        """
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
        """
        Get the target path for exploration.
        """
        return self.look_on or self.root

    @lazyfield
    def resolver(self) -> PathConverter:
        """
        Get the path converter based on the root path.

        Returns:
            PathConverter: The path converter function.
        """
        return make_modulename_resolver(self.root)

    def _itermod(self, path: pathlib.Path):
        """
        Iterate through a module using the given resolver.

        Args:
            path (pathlib.Path): The path to the module.

        Yields:
            tuple[str, Any]: A tuple containing the name and object of each item in the module.
        """
        yield from (
            (name, obj)
            for name, obj in iterate_module(path, self.resolver)
            if self.validator(obj)
        )

    def _iterdir(
        self, path: pathlib.Path
    ) -> typing.Generator[tuple[str, typing.Any], None, None]:
        """
        Iterate through a directory, exploring subdirectories and modules.

        Args:
            path (pathlib.Path): The path to the directory.

        Yields:
            tuple[str, Any]: A tuple containing the name and object of each item in the directory.
        """
        for item in path.iterdir():
            if not self._should_look(item):
                continue
            if item.is_dir():
                yield from self._iterdir(item)
            else:
                yield from self._itermod(item)


def class_validator(*types: type) -> Validator:
    """
    Create a class validator that checks if objects are subclasses of the provided types.

    Args:
        *types (type): Types to validate against.

    Returns:
        Validator: The validator function.
    """
    if not types:
        raise MissingParams("Missing types in class_validator paramaters")

    def validator(obj: typing.Any):
        return (
            issubclass(obj, types) and obj not in types
            if inspect.isclass(obj)
            else False
        )

    return validator


def instance_validator(*types: type) -> Validator:
    """
    Create an instance validator that checks if objects are instances of the provided types.

    Args:
        *types (type): Types to validate against.

    Returns:
        Validator: The validator function.
    """
    if not types:
        raise MissingParams("Missing types in instance_validator paramaters")

    def validator(obj: typing.Any):
        return isinstance(obj, types)

    return validator


class FinderBuilder:
    """
    Builder class to construct a Finder instance with various configurations.
    """

    def __init__(self) -> None:
        self.root: typing.Optional[pathlib.Path] = None
        self._validators = []
        self._lock = threading.Lock()
        self._exclude = []

    def reset(self) -> None:
        """
        Reset the builder to its initial state.
        """
        with self._lock:
            self.root = None
            self._validators = []
            self._exclude = []

    def from_path(self, path: pathlib.Path) -> Self:
        """
        Set the root path for the finder from a provided path.

        Args:
            path (pathlib.Path): The root path.

        Returns:
            FinderBuilder: The FinderBuilder instance.

        Raises:
            InvalidPath: If the path does not exist
        """
        if not path.exists():
            raise InvalidPath(f"root must be a valid path, received {path}")
        self.root = path
        return self

    def from_cwd(self) -> Self:
        """
        Set the root path for the finder to the current working directory.

        Returns:
            FinderBuilder: The FinderBuilder instance.
        """
        return self.from_path(pathlib.Path.cwd())

    def from_project(self) -> Self:
        """
        Set the root path for the finder to the project root.

        Returns:
            FinderBuilder: The FinderBuilder instance.
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

    def from_package(self, stack_position: int = 1) -> Self:
        """
        Set the root path for the finder to the calling package root.

        Args:
            stack_position (int, optional): The position in the stack trace of the calling function (default: 1).

        Returns:
            FinderBuilder: The FinderBuilder instance.
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

    def _make_validator(self) -> Validator:
        validators = [*self._validators]

        def _validator(obj: typing.Any):
            return all(validator(obj) for validator in validators)

        return _validator

    def add_validator(self, validator: Validator) -> Self:
        """
        Add a validation function to the builder.

        Args:
            validator (Validator): The validation function to add.

        Returns:
            FinderBuilder: The FinderBuilder instance.
        """
        with self._lock:
            self._validators.append(validator)
        return self

    def child_of(self, *types: type) -> Self:
        """
        Add a class validator that checks if objects are subclasses of the provided types.

        Args:
            *types (type): Types to validate against.

        Returns:
            FinderBuilder: The FinderBuilder instance.
        """
        return self.add_validator(class_validator(*types))

    def instance_of(self, *types: type) -> Self:
        """
        Add an instance validator that checks if objects are instances of the provided types.

        Args:
            *types (type): Types to validate against.

        Returns:
            FinderBuilder: The FinderBuilder instance.
        """
        return self.add_validator(instance_validator(*types))

    def exclude(self, *paths: StrOrPath) -> Self:
        """
        Exclude paths from search.

        Args:
            *paths (StrOrPath): Paths to exclude.

        Returns:
            FinderBuilder: The FinderBuilder instance.
        """
        self._exclude.extend(paths)
        return self

    def exclude_default(self) -> Self:
        """
        Exclude default paths (e.g., '__init__.py', '__pycache__') from search.

        Returns:
            FinderBuilder: The FinderBuilder instance.
        """
        return self.exclude("__init__.py", "__pycache__")

    def build(
        self,
        look_on: typing.Optional[pathlib.Path] = None,
    ) -> _Finder:
        """
        Build a Finder instance with the provided configurations.

        Args:
            look_on (Optional[pathlib.Path], optional): The path to focus the search on (default: None).

        Returns:
            _Finder: The built Finder instance.
        """
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
    ) -> dict[str, typing.Any]:
        """
        Find and return located objects using the provided configurations.

        Args:
            look_on (Optional[pathlib.Path], optional): The path to focus the search on (default: None).

        Returns:
            dict: The dictionary containing the located objects.
        """
        if self.root is None:
            self.from_project()
            assert self.root is not None
        return self.build(look_on).find()


finder_builder = FinderBuilder()
