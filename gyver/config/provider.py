from contextlib import suppress
from typing import Any
from typing import Iterable
from typing import TypeVar
from typing import get_args
from typing import get_origin

from pydantic.fields import ModelField

from gyver.config.utils import boolean_cast
from gyver.exc import MissingName
from gyver.model import Model
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

    fields = tuple(
        field
        for field in _get_fields(provider)
        if field.name not in (*presets, "__prefix__", "__without_prefix__")
    )
    result = {
        field.alias: _get_value(provider, field, __config__)
        for field in fields
    }
    return provider.parse_obj(result | presets)


def _get_fields(provider: type[ProviderT]) -> Iterable[ModelField]:
    return provider.__fields__.values()


def _get_value(
    provider: type[ProviderConfig], field: ModelField, config: Config
):
    name, alias = _make_names(provider, field)
    default = _get_default(field)
    cast = _get_cast(field)
    return _tryeach(alias, name, default=default, cast=cast, config=config)


def _tryeach(*names: str, default: Any, cast: Any, config: Config) -> Any:
    for name in names:
        with suppress(MissingName):
            return config(name, cast, default)
    raise panic(
        MissingName, f"{','.join(names)} not found and no default was given"
    )


def _make_names(
    provider: type[ProviderConfig], field: ModelField
) -> tuple[str, str]:
    name = field.name
    alias = field.alias
    if not provider.__prefix__ or {name, alias}.intersection(
        provider.__without_prefix__
    ):
        return (name, alias)
    prefix = provider.__prefix__.removesuffix("_")
    name = name.removeprefix("_")
    alias = alias.removeprefix("_")
    return f"{prefix}_{name}".upper(), f"{prefix}_{alias}".upper()


def _get_cast(field: ModelField):
    _sequences = (list, tuple, set)
    outer_type = field.outer_type_
    origin = get_origin(outer_type)
    if outer_type is bool:
        return boolean_cast
    if not origin:
        return (
            make_lex_separator(outer_type)
            if outer_type in _sequences
            else outer_type
        )
    if (origin := get_origin(outer_type)) in _sequences:
        assert origin is not None
        args = get_args(outer_type)
        cast = args[0] if args else str
        return make_lex_separator(origin, cast)
    if dict in (origin, outer_type):
        raise NotImplementedError("Unable to handle dict-like variables")
    return origin


def _get_default(field: ModelField):
    if field.default not in (None, Ellipsis):
        return field.default
    return (
        MISSING if field.default_factory is None else field.default_factory()
    )
