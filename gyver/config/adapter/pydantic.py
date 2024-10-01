from typing import Any
from collections.abc import Generator
from collections.abc import Sequence
from typing import cast

from config import MISSING
from gyver.attrs import define
from lazyfields import lazyfield
from pydantic import BaseModel
from pydantic import v1
from pydantic.fields import FieldInfo

from gyver.config.adapter.interface import FieldResolverStrategy


@define
class FieldWrapper:
    name: str
    field_info: FieldInfo


@define
class PydanticResolverStrategy(FieldResolverStrategy[FieldWrapper]):
    field: FieldWrapper

    @lazyfield
    def field_info(self) -> FieldInfo:
        return self.field.field_info

    def cast(self) -> type:
        return cast(type, self.field_info.annotation)

    def names(self) -> Sequence[str]:
        return (self.field.name, self.field_info.alias or self.field.name)

    def init_name(self) -> str:
        return self.field.name

    def default(self) -> Any | type[MISSING]:
        if self.field_info.default not in (None, Ellipsis):
            return self.field_info.default
        return (
            MISSING
            if self.field_info.default_factory is None
            else self.field_info.default_factory
        )

    @classmethod
    def iterfield(
        cls,
        config_class: type[BaseModel | v1.BaseModel],
    ) -> Generator[FieldWrapper, Any, Any]:
        if issubclass(config_class, v1.BaseModel):
            yield from cls._as_v1_iterfield(config_class)
        else:
            yield from map(
                lambda item: FieldWrapper(*item), config_class.model_fields.items()
            )

    @classmethod
    def _as_v1_iterfield(
        cls, config_class: type[v1.BaseModel]
    ) -> Generator[FieldWrapper, Any, Any]:
        for field in config_class.__fields__.values():
            field_info = FieldInfo(
                annotation=field.outer_type_,
                default=field.default,
                default_factory=field.default_factory,
                alias=field.alias,
            )
            fw = FieldWrapper(field.name, field_info)
            yield fw
