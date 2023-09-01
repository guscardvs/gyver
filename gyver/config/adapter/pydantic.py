from typing import Any
from typing import Generator
from typing import Sequence
from typing import Union
from typing import cast

from config import MISSING
from gyver.attrs import define
from gyver.model import is_v2
from lazyfields import lazyfield
from pydantic import BaseModel

if is_v2:
    from pydantic.v1.fields import ModelField
else:
    from pydantic.fields import ModelField  # type: ignore

from gyver.config.adapter.interface import FieldResolverStrategy


@define
class PydanticResolverStrategy(FieldResolverStrategy[ModelField]):
    field: ModelField

    def cast(self) -> type:
        return self.field.outer_type_

    def names(self) -> Sequence[str]:
        return (self.field.name, self.field.alias)

    def init_name(self) -> str:
        return self.field.name

    def default(self) -> Union[Any, type[MISSING]]:
        if self.field.default not in (None, Ellipsis):
            return self.field.default
        return (
            MISSING
            if self.field.default_factory is None
            else self.field.default_factory
        )

    @staticmethod
    def iterfield(
        config_class: type[BaseModel],
    ) -> Generator[ModelField, Any, Any]:
        yield from config_class.__fields__.values()


if is_v2:
    from pydantic.fields import FieldInfo
    from pydantic import v1

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

        def default(self) -> Union[Any, type[MISSING]]:
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
            config_class: type[Union[BaseModel, v1.BaseModel]],
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
                print(fw)
                yield fw
