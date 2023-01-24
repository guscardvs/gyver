import typing

import sqlalchemy as sa

from . import interface

T = typing.TypeVar("T")


def _make_converter(
    converter: typing.Callable[[interface.FieldType], interface.FieldType],
):
    def _converter(
        comparator: interface.Comparator[T],
    ) -> interface.Comparator[T]:
        def _comp(field: interface.FieldType, target: T) -> interface.Comparison:
            return comparator(converter(field), target)

        return _comp

    return _converter


as_date = _make_converter(sa.func.date)
as_time = _make_converter(sa.func.time)
as_lower = _make_converter(sa.func.lower)
as_upper = _make_converter(sa.func.upper)

__all__ = ["as_date", "as_time", "as_lower", "as_upper"]
