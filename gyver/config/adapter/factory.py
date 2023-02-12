from contextlib import suppress
from dataclasses import is_dataclass
from pathlib import Path
from typing import Any
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import TypeVar
from typing import get_args
from typing import get_origin

from pydantic import BaseModel

from gyver.config.config import Config
from gyver.config.utils import boolean_cast
from gyver.exc import MissingName
from gyver.utils import finder
from gyver.utils import json
from gyver.utils import panic
from gyver.utils.strings import make_lex_separator

from .attrs import AttrsResolverStrategy
from .dataclass import DataclassResolverStrategy
from .interface import FieldResolverStrategy
from .mark import is_config
from .pydantic import PydanticResolverStrategy

_default_config = Config()

T = TypeVar("T")


def _try_each(*names: str, default: Any, cast: Any, config: Config):
    for name in names:
        with suppress(MissingName):
            return config(name, cast, default)
    raise panic(MissingName, f"{', '.join(names)} not found and no default was given")


def _resolve_cast(outer_type: type):
    _sequences = (list, tuple, set)
    origin = get_origin(outer_type)
    if outer_type is bool:
        return boolean_cast
    if origin is None:
        return (
            make_lex_separator(outer_type) if outer_type in _sequences else outer_type
        )
    if (origin := get_origin(outer_type)) in _sequences:
        args = get_args(outer_type)
        cast = args[0] if args else str
        return make_lex_separator(origin, cast)  # type: ignore
    return _loads if dict in (origin, outer_type) else origin


def _loads(val: Any) -> Any:
    return json.loads(val) if isinstance(val, str) else val


class AdapterConfigFactory:
    def __init__(self, config: Config = _default_config) -> None:
        self._config = config

    def get_strategy_class(self, config_class: type) -> type[FieldResolverStrategy]:
        if is_dataclass(config_class):
            return DataclassResolverStrategy
        elif issubclass(config_class, BaseModel):
            return PydanticResolverStrategy
        elif hasattr(config_class, "__attrs_attrs__"):
            return AttrsResolverStrategy
        raise ValueError("Unknown class definition")

    def load(
        self,
        model_cls: type[T],
        __prefix__: str = "",
        *,
        presets: Optional[Mapping[str, Any]] = None,
        **defaults: Any,
    ) -> T:
        presets = presets or {}
        strategy_class = self.get_strategy_class(model_cls)
        resolvers = tuple(
            resolver
            for field in strategy_class.iterfield(model_cls)
            if (resolver := strategy_class(field)).init_name() not in presets
        )
        result = {
            resolver.init_name(): self._get_value(
                model_cls, resolver, __prefix__, defaults
            )
            for resolver in resolvers
        }
        return model_cls(**result | presets)

    def _get_value(
        self,
        model_cls: type,
        resolver: FieldResolverStrategy,
        prefix: str,
        defaults: Mapping[str, Any],
    ):
        names = self.resolve_names(model_cls, resolver, prefix)
        default = next(
            (result for name in names if (result := defaults.get(name))),
            resolver.default(),
        )
        cast = _resolve_cast(resolver.cast())
        return _try_each(*names, default=default, cast=cast, config=self._config)

    def resolve_names(
        self, model_cls: type, resolver: FieldResolverStrategy, prefix: str
    ) -> Sequence[str]:
        names = resolver.names()
        prefix = prefix or getattr(model_cls, "__prefix__", "")
        prefix = prefix.removesuffix("_")
        without_prefix = getattr(model_cls, "__without_prefix__", ())
        if not prefix or set(names).intersection(without_prefix):
            return (*names, *map(str.upper, names))

        processed_names = []
        for name in names:
            name.lstrip("_")
            processed = f"{prefix}_{name}".lower()
            processed_names.extend((processed, processed.upper()))

        return tuple(processed_names)

    @classmethod
    def resolve_confignames(
        cls,
        root: Path,
    ) -> dict[type, tuple[Sequence[str], ...]]:
        """
        The resolve_confignames function resolves the names of all environment
        variables required by the configs in any class marked as config.
        It returns them in a dict of {class: (configs)}.

        :param cls: Call the class_validator function, which is used to validate that a
        class has all of the required attributes
        :param root: Path: Specify the root directory of the project
        :return: A dictionary of {class: (configs)}
        """
        provider_finder = finder.Finder(is_config, root)
        provider_finder.find()
        tempself = cls()
        return {
            provider: tuple(
                tempself.resolve_names(provider, field, "")
                for field in provider.__fields__.values()
            )
            for provider in provider_finder.output.values()
        }
