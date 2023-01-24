import enum
import typing
from dataclasses import dataclass

from sqlalchemy.sql import ColumnElement
from sqlalchemy.sql import Select


class OrderDirection(enum.Enum):
    ASC = "asc"
    DESC = "desc"


@dataclass(frozen=True)
class OrderBy:
    __slots__ = ("field", "direction")

    field: typing.Optional[str]
    direction: OrderDirection

    @property
    def _should_apply(self):
        return self.field is not None

    @classmethod
    def none(cls):
        return cls(field=None, direction=OrderDirection.ASC)

    @classmethod
    def asc(cls, field: str):
        return cls(field, OrderDirection.ASC)

    @classmethod
    def desc(cls, field: str):
        return cls(field, OrderDirection.DESC)

    def apply(self, query: Select) -> Select:
        return (
            query.order_by(self._apply_order(self._find_column(query)))
            if self._should_apply
            else query
        )

    def _find_column(self, query: Select) -> ColumnElement:
        try:
            return next(col for col in query.selected_columns if col.key == self.field)
        except StopIteration:
            raise ValueError(f"Field {self.field} does not exist in query") from None

    def _apply_order(self, col: ColumnElement):
        return col.asc() if self.direction is OrderDirection.ASC else col.desc()
