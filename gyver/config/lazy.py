import inspect
import sys
from types import ModuleType
from typing import Any
from typing import Callable
from typing import Generic
from typing import Sequence
from typing import TypeVar
from typing import Union
from typing import overload

from config.interface import MISSING
from config.interface import ConfigLike
from config.interface import _default_cast
from gyver.attrs import define

from gyver.utils.lazy import lazyfield

ConfigT = TypeVar("ConfigT", bound=ConfigLike)


@define
class EnvParam:
    """
    Represents an environment parameter.

    :param name: The name of the parameter.
    :param cast: A callable that casts the parameter value to the desired type.
    :param default: The default value of the parameter.
    :param frame_info: Frame information indicating where the parameter is defined.
    """

    name: str
    cast: Callable[[str], Any]
    default: Any
    frame_info: inspect.FrameInfo


T = TypeVar("T")


class LazyVal:
    def __init__(self, env_param: EnvParam, lazy_cfg: "LazyConfig") -> None:
        """
        Represents a lazily evaluated configuration value.

        :param env_param: The associated environment parameter.
        :param lazy_cfg: The parent LazyConfig object.
        """
        self.__env_param__ = env_param
        self.__lazy_cfg__ = lazy_cfg

    def __getattribute__(self, name: str) -> Any:
        """
        Retrieves the attribute value.

        :param name: The name of the attribute.
        :return: The attribute value.
        """
        if name in {"__env_param__", "__lazy_cfg__"}:
            return object.__getattribute__(self, name)
        resolved = self.__lazy_cfg__.resolve_param(self)
        return object.__getattribute__(resolved, name)


@define
class LazyConfig(Generic[ConfigT]):
    """
    Represents a lazily evaluated configuration.

    :param config: The configuration object.
    """

    config: ConfigT

    @lazyfield
    def inner_vals(self) -> list[LazyVal]:
        """
        Lazily evaluated values.

        :return: The list of lazily evaluated values.
        """
        return []

    def _get_stack(self):
        """
        Returns the next frame in the stack that is not from the current file.

        :return: The frame information.
        """
        return next(item for item in inspect.stack() if item.filename != __file__)

    def get(
        self,
        name: str,
        cast: Callable = _default_cast,
        default: Union[Any, type[MISSING]] = MISSING,
    ) -> Any:
        """
        Retrieves the lazily evaluated value.

        :param name: The name of the value.
        :param cast: A callable that casts the value to the desired type.
        :param default: The default value if the parameter is missing.
        :return: The lazily evaluated value.
        """
        lazyval = LazyVal(EnvParam(name, cast, default, self._get_stack()), self)
        self.inner_vals.append(lazyval)
        return lazyval

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
        """
        Retrieves the lazily evaluated value.

        :param name: The name of the value.
        :param cast: A callable that casts the value to the desired type.
        :param default: The default value if the parameter is missing.
        :return: The lazily evaluated value.
        """
        return self.get(name, cast, default)

    @lazyfield
    def modcache(self) -> dict[ModuleType, Sequence[tuple[str, Any]]]:
        """
        Cached module members.

        :return: The dictionary mapping modules to their members.
        """
        return {}

    def _get_members(self, mod: ModuleType) -> Sequence[tuple[str, Any]]:
        """
        Retrieves the members of the given module.

        :param mod: The module object.
        :return: The sequence of module members.
        """
        if mod in self.modcache:
            return self.modcache[mod]
        self.modcache[mod] = inspect.getmembers(mod)
        return self.modcache[mod]

    def resolve_param(self, lazyval: "LazyVal"):
        """
        Resolves the lazily evaluated parameter.

        :param lazyval: The LazyVal object.
        :return: The resolved value.
        """
        envparam = lazyval.__env_param__
        mod = sys.modules[envparam.frame_info.frame.f_globals["__name__"]]
        resolved = self.config.get(envparam.name, envparam.cast, envparam.default)
        for key, value in self._get_members(mod):
            if getattr(value, "__env_param__", None) is envparam:
                setattr(mod, key, resolved)
        return resolved

    def resolve(self):
        """
        Resolves all the lazily evaluated parameters.
        """
        for val in self.inner_vals:
            self.resolve_param(val)
        self.modcache.clear()

    def expected(self) -> list[EnvParam]:
        """
        Retrieves the list of expected environment parameters.

        :return: The list of expected environment parameters.
        """
        return [item.__env_param__ for item in self.inner_vals]
