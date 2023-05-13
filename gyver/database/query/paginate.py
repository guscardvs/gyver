from abc import ABC
from abc import abstractmethod

from gyver.attrs import define
from sqlalchemy.sql import Select

from gyver.database.typedef import ClauseType

from . import comp as cp
from .interface import ApplyClause
from .interface import Comparator
from .where import Where


@define
class Paginate(ApplyClause, ABC):
    type_ = ClauseType.APPLY
    limit: int
    offset: int

    @abstractmethod
    def apply(self, query: Select) -> Select:
        raise NotImplementedError

    @staticmethod
    def none():
        return _NullPaginate(limit=0, offset=0)

    def __bool__(self):
        return isinstance(self, _NullPaginate)


class LimitOffsetPaginate(Paginate):
    def apply(self, query: Select) -> Select:
        return query.limit(self.limit).offset(self.offset)


@define
class FieldPaginate(Paginate):
    field: str = "id"
    jump_comparison: Comparator = cp.greater

    def apply(self, query: Select) -> Select:
        return query.where(
            Where(self.field, self.offset, self.jump_comparison).bind(
                query.selected_columns  # type: ignore
            )
        ).limit(self.limit)


class _NullPaginate(Paginate):
    def apply(self, query: Select) -> Select:
        return query
