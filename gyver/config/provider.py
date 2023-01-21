from contextlib import suppress
from pathlib import Path
from typing import Any, Optional, Sequence
from typing import TypeVar
from typing import get_args
from typing import get_origin

from pydantic.fields import ModelField

from gyver.config.utils import boolean_cast
from gyver.exc import MissingName
from gyver.model import Model
from gyver.utils import finder, json
from gyver.utils.exc import panic
from gyver.utils.strings import make_lex_separator

from .config import MISSING
from .config import Config


class ProviderConfig(Model):
    __prefix__ = ""
    __without_prefix__ = ()

    class Config:
        alias_generator = str.upper
        fields = {"exclude": {}}


ProviderT = TypeVar("ProviderT", bound=ProviderConfig)

_default_config = Config()


def from_config(
    provider: type[ProviderT],
    *,
    __config__: Config = _default_config,
    **presets: Any,
) -> ProviderT:
    return ConfigLoader(__config__).load(provider, **presets)


def _tryeach(*names: str, default: Any, cast: Any, config: Config) -> Any:
    for name in names:
        with suppress(MissingName):
            return config(name, cast, default)
    raise panic(
        MissingName, f"{', '.join(names)} not found and no default was given"
    )


def _get_cast(field: ModelField):
    _sequences = (list, tuple, set)
    outer_type = field.outer_type_
    origin = get_origin(outer_type)
    if outer_type is bool:
        return boolean_cast
    if origin is None:
        return (
            make_lex_separator(outer_type)
            if outer_type in _sequences
            else outer_type
        )
    if (origin := get_origin(outer_type)) in _sequences:
        args = get_args(outer_type)
        cast = args[0] if args else str
        return make_lex_separator(origin, cast)  # type: ignore
    return json.loads if dict in (origin, outer_type) else origin


def _get_default(field: ModelField):
    if field.default not in (None, Ellipsis):
        return field.default
    return (
        MISSING if field.default_factory is None else field.default_factory()
    )


class ConfigLoader:
    def __init__(
        self,
        config: Config = _default_config,
        prefix: Optional[str] = None,
        without_prefix: Sequence[str] = (),
    ):
        self._config = config
        self._prefix = prefix
        self._without_prefix = without_prefix

    def load(self, model_cls: type[ProviderT], **presets: Any) -> ProviderT:
        self._without_prefix = (
            *self._without_prefix,
            *model_cls.__without_prefix__,
        )
        fields = tuple(
            field
            for field in model_cls.__fields__.values()
            if field.name not in (*presets, "__without_prefix__")
        )
        result = {
            field.alias: self._get_value(model_cls, field) for field in fields
        }
        return model_cls.parse_obj(result | presets)

    def _get_value(self, model_cls: type, field: ModelField):
        names = self.resolve_names(model_cls, field)
        default = _get_default(field)
        cast = _get_cast(field)
        return _tryeach(
            *names, default=default, cast=cast, config=self._config
        )

    def resolve_names(
        self, model_cls: type[ProviderConfig], field: ModelField
    ) -> tuple[str, ...]:
        name = field.name
        alias = field.alias
        prefix = (
            self._prefix if self._prefix is not None else model_cls.__prefix__
        )
        prefix = prefix.removesuffix("_")
        if not prefix or {name, alias}.intersection(self._without_prefix):
            return (name, alias)
        name = name.removeprefix("_")
        alias = alias.removeprefix("_")
        default_results = (
            f"{prefix}_{name}".upper(),
            f"{prefix}_{alias}".upper(),
        )
        return (*default_results, *(item.lower() for item in default_results))

    @classmethod
    def resolve_confignames(
        cls,
        root: Path,
    ) -> dict[type[ProviderConfig], tuple[tuple[str, str], ...]]:
        """resolves confignames and returns in a dict of {class: (configs)}"""
        validator = finder.class_validator(ProviderConfig)
        provider_finder = finder.Finder(validator, root)
        provider_finder.find()
        tempself = cls()
        return {
            provider: tuple(
                tempself.resolve_names(provider, field)
                for field in provider.__fields__.values()
            )
            for provider in provider_finder.output.values()
        }
