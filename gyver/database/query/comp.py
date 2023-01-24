import typing

import sqlalchemy as sa

from gyver.database.query.null import NullBind

from .interface import BindClause
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
    fmt = {"like": "%{target}%", "rlike": "%{target}", "llike": "{target}%"}[opt]

    def comparator(field: FieldType, target: str):
        return field.ilike(fmt.format(target=target))

    return comparator


def isnull(field: FieldType, target: bool) -> Comparison:
    return field.is_(None) if target else field.is_not(None)


def includes(field: FieldType, target: typing.Sequence) -> Comparison:
    return field.in_(list(target))


def excludes(field: FieldType, target: typing.Sequence) -> Comparison:
    return field.not_in(list(target))


def json_contains(field: FieldType, target: typing.Any) -> Comparison:
    return sa.func.json_contains(field, f'"{target}"')


def json_empty(field: FieldType, target: typing.Any) -> Comparison:
    func_length = sa.func.json_length(field)
    return func_length == 0 if target else func_length != 0


def make_relation_check(clause: BindClause) -> Comparator:
    def _relation_exists(field: FieldType, target: bool) -> Comparison:
        comp = clause.bind(field.class_)
        func = (
            field.has
            if field.property.direction.name.lower() not in ("onetomany", "manytomany")
            else field.any
        )
        result = func() if str(comp) == str(sa.true()) else func(comp)
        return result if target else ~result

    return _relation_exists


# Compat
relation_exists = relation_exists_m2m = relation_exists_o2m = make_relation_check(
    NullBind()
)
