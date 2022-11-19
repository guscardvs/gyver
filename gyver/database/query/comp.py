import typing

import sqlalchemy as sa

from .interface import Comparator
from .interface import Comparison
from .interface import FieldType
from .interface import Sortable


def always_true(field: FieldType, target: typing.Any) -> Comparison:
    del field, target
    return sa.true()


def equals(field: FieldType, target: typing.Any) -> Comparison:
    return field == target


def not_equals(field: FieldType, target: typing.Any) -> Comparison:
    return field != target


def greater(field: FieldType, target: Sortable) -> Comparison:
    return field > target


def greater_equals(field: FieldType, target: Sortable) -> Comparison:
    return field >= target


def lesser(field: FieldType, target: Sortable) -> Comparison:
    return field < target


def lesser_equals(field: FieldType, target: Sortable) -> Comparison:
    return field <= target


def between(field: FieldType, target: tuple[Sortable, Sortable]) -> Comparison:
    left, right = target
    return field.between(left, right)


def range(field: FieldType, target: tuple[Sortable, Sortable]) -> Comparison:
    left, right = target
    return sa.and_(greater_equals(field, left), (lesser(field, right)))


def like(field: FieldType, target: str) -> Comparison:
    return field.like(f"%{target}%")


def rlike(field: FieldType, target: str) -> Comparison:
    return field.like(f"{target}%")


def llike(field: FieldType, target: str) -> Comparison:
    return field.like(f"%{target}")


def insensitive_like(
    opt: typing.Literal["like", "rlike", "llike"] = "like"
) -> Comparator[str]:
    fmt = {"like": "%{target}%", "rlike": "%{target}", "llike": "{target}%"}[
        opt
    ]

    def comparator(field: FieldType, target: str):
        return field.ilike(fmt.format(target=target))

    return comparator


def isnull(field: FieldType, val: bool) -> Comparison:
    return field.is_(None) if val else field.is_not(None)
