import typing
from abc import ABC
from abc import abstractmethod

from sqlalchemy.sql import Select

from gyver.database.typedef import ClauseType
from gyver.utils.helpers import cache

from . import comp as cp
from .interface import ApplyClause
from .interface import Comparator
from .where import Where


class Paginate(ApplyClause, ABC):
    type_ = ClauseType.APPLY

    @typing.final
    def __init__(self, limit: int, offset: int) -> None:
        self._limit = limit
        self._offset = offset

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
        return query.limit(self._limit).offset(self._offset)


@cache
def make_field_paginate(
    field: str, jump_comparison: Comparator = cp.greater
) -> type[Paginate]:
    class FieldPaginate(Paginate):
        def apply(self, query: Select) -> Select:
            return query.where(
                Where(field, self._offset, jump_comparison).bind(
                    query.selected_columns  # type: ignore
                )
            ).limit(self._limit)

    return FieldPaginate


IdPaginate = make_field_paginate("id")


class _NullPaginate(Paginate):
    def apply(self, query: Select) -> Select:
        return query
