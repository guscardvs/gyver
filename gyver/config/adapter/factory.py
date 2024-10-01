import contextlib
import typing
from contextlib import suppress
from dataclasses import is_dataclass
from pathlib import Path
from typing import (
    Any,
    TypeVar,
    cast,
    get_args,
    get_origin,
)
from collections.abc import Callable, Mapping, Sequence

from config import MISSING, Config
from config.exceptions import MissingName
from config.interface import ConfigLike
from config.utils import LiteralType, boolean_cast, literal_cast

from gyver.attrs import define, mark_factory
from gyver.attrs.utils.functions import disassemble_type
from gyver.attrs.utils.typedef import DisassembledType
from gyver.misc import autodiscovery
from gyver.misc.strings import make_lex_separator
from gyver.utils import json, panic

from .dataclass import DataclassResolverStrategy
from .gattrs import GyverAttrsResolverStrategy
from .interface import FieldResolverStrategy
from .mark import is_config

_DEFAULT_CONFIG = Config()

T = TypeVar("T")


def _try_each(*names: str, default: Any, cast: Any, config: ConfigLike):
    for name in names:
        with suppress(MissingName):
            return config(name, cast)
    if default is not MISSING:
        return default
    raise panic(MissingName, f"{', '.join(names)} not found and no default was given")


def _resolve_cast(outer_type: type) -> tuple[Any, bool]:
    _sequences = (list, tuple, set)
    origin = get_origin(outer_type)
    if outer_type is bool:
        return boolean_cast, False
    if isinstance(outer_type, typing.cast(Any, LiteralType)):
        return literal_cast(outer_type), False
    with contextlib.suppress(ValueError):
        AdapterConfigFactory.get_strategy_class(disassemble_type(outer_type))
        return outer_type, True
    if origin is None:
        return (
            make_lex_separator(outer_type) if outer_type in _sequences else outer_type
        ), False
    if (origin := get_origin(outer_type)) in _sequences:
        assert origin is not None
        args = get_args(outer_type)
        cast = args[0] if args else str
        return make_lex_separator(origin, cast), False
    return (
        _loads if dict in (origin, outer_type) else origin,  # type:ignore
        False,
    )


def _loads(val: Any) -> Any:
    return json.loads(val) if isinstance(val, str) else val


@define
class AdapterConfigFactory:
    """
    Factory for creating configuration instances based on model classes.
    """

    config: ConfigLike = _DEFAULT_CONFIG

    @staticmethod
    def get_strategy_class(
        config_class: DisassembledType,
    ) -> type[FieldResolverStrategy]:
        """
        Get the appropriate strategy class for resolving fields in the configuration class.

        Args:
            config_class (type): The configuration class to resolve.

        Returns:
            type[FieldResolverStrategy]: The strategy class for resolving fields.
        """
        klass = config_class.origin or config_class.type_
        try:
            from pydantic import BaseModel, v1

            base_model_cls = [BaseModel, v1.BaseModel]
        except ImportError:
            base_model_cls = []
        if hasattr(klass, "__gyver_attrs__"):
            return GyverAttrsResolverStrategy
        elif is_dataclass(klass):
            return DataclassResolverStrategy
        elif base_model_cls and issubclass(klass, tuple(base_model_cls)):
            from .pydantic import PydanticResolverStrategy

            return PydanticResolverStrategy
        elif hasattr(klass, "__attrs_attrs__"):
            from .attrs import AttrsResolverStrategy

            return AttrsResolverStrategy
        raise ValueError("Unknown class definition")

    def load(
        self,
        model_cls: type[T],
        __prefix__: str = "",
        __sep__: str = "__",
        *,
        presets: dict[str, Any] | None = None,
        **defaults: Any,
    ) -> T:
        """
        Load a configuration instance based on a model class.

        Args:
            model_cls (type[T]): The model class representing the configuration.
            __prefix__ (str): Optional prefix for configuration fields.
            __set__(str): Optional prefix to separate fields of nested models. Default is "__"
            presets (Optional[dict[str, Any]]): Optional preset values for fields.
            **defaults (Any): Default values for fields.

        Returns:
            T: The loaded configuration instance.
        """
        presets = presets or {}
        strategy_class = self.get_strategy_class(disassemble_type(model_cls))
        resolvers = tuple(
            resolver
            for field in strategy_class.iterfield(model_cls)
            if (resolver := strategy_class(field)).init_name() not in presets
        )
        result = {
            resolver.init_name(): self._get_value(
                model_cls,
                resolver,
                __prefix__,
                __sep__,
                defaults,
            )
            for resolver in resolvers
        }
        return model_cls(**result | presets)

    def maker(
        self,
        model_cls: type[T],
        __prefix__: str = "",
        __sep__: str = "__",
        *,
        presets: dict[str, Any] | None = None,
        **defaults: Any,
    ) -> Callable[[], T]:
        """
        Create a factory function for loading configuration instances.

        Args:
            model_cls (type[T]): The model class representing the configuration.
            __prefix__ (str): Optional prefix for configuration fields.
            presets (Optional[dict[str, Any]]): Optional preset values for fields.
            **defaults (Any): Default values for fields.

        Returns:
            Callable[[], T]: The factory function for loading configuration instances.
        """

        @mark_factory
        def load():
            return self.load(
                model_cls, __prefix__, __sep__, presets=presets, **defaults
            )

        return load

    def _get_value(
        self,
        model_cls: type,
        resolver: FieldResolverStrategy,
        prefix: str,
        sep: str,
        defaults: Mapping[str, Any],
    ):
        names = self.resolve_names(model_cls, resolver, prefix)
        default = next(
            (result for name in names if (result := defaults.get(name))),
            resolver.default(),
        )
        cast, _is_config = _resolve_cast(resolver.cast())
        if _is_config:
            return self.load(
                cast,
                f"{next(iter(names))}{sep}",
                sep,
                defaults=defaults,
            )
        return _try_each(*names, default=default, cast=cast, config=self.config)

    def resolve_names(
        self, model_cls: type, resolver: FieldResolverStrategy, prefix: str
    ) -> Sequence[str]:
        names = resolver.names()
        prefix = prefix or getattr(model_cls, "__prefix__", "")
        without_prefix = cast(
            Sequence[str], getattr(model_cls, "__without_prefix__", ())
        )
        if not prefix or set(names).intersection(without_prefix):
            return (*names, *map(str.upper, names))

        processed_names = []
        for name in names:
            _prefix = f"{prefix}_" if not prefix.endswith("_") else prefix
            processed = f"{_prefix}{name}".lower()
            processed_names.extend((processed, processed.upper()))

        return tuple(processed_names)

    @classmethod
    def resolve_confignames(
        cls,
        root: Path,
    ) -> dict[type, tuple[Sequence[str], ...]]:
        """
        Resolve the environment variable names required by marked config classes.

        Args:
            root (Path): The root directory of the project.

        Returns:
            dict[type, tuple[Sequence[str], ...]]: A dictionary of config classes and their associated environment variable names.
        """
        builder = autodiscovery.RuntimeAutoDiscovery(is_config, root)
        output = builder.load_asdict()
        tempself = cls()
        return {
            cfg: tuple(
                tempself.resolve_names(cfg, field, "")
                for field in cfg.__fields__.values()
            )
            for cfg in output.values()
        }
