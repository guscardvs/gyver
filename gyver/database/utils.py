import typing
from functools import partial
from types import FunctionType
from urllib.parse import quote

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from gyver.database import default_metadata
from gyver.url.netloc import Netloc
from gyver.utils import cache
from gyver.url import URL

from . import drivers
from .config import DatabaseConfig


@cache
def make_uri(config: DatabaseConfig, sync: bool = False) -> str:
    """Construct a database URI from a database configuration .

    Args:
        config (DatabaseConfig): configuration object containing information about the
        database such as dialect, host, username, password, etc.
        sync (bool, optional): If uses async or sync drivers. Defaults to False.

    Returns:
        str: database URI in the format
        'dialect_name(+driver)?://username:password@host:port/dbname'
        if not only host else 'dialect_name(+driver)?://host'
    """

    url = URL("").set(netloc=config.host)
    url.scheme = f"{drivers.build_dialect_scheme(config.dialect, sync)}"

    if config.dialect.only_host:
        return url.encode()

    return url.add(
        path=config.name,
        netloc_args=Netloc("").set(
            username=config.user,
            password=config.password,
            port=config.effective_port,
        ),
    ).encode()


EntityT = typing.TypeVar("EntityT")
CallableT = typing.TypeVar("CallableT", bound=typing.Callable)


@typing.overload
def make_relation(
    relation: typing.Union[str, type[EntityT]],
    *,
    relation_name: str = "",
    back_populates: typing.Optional[str] = None,
    secondary: typing.Union[sa.Table, type, None] = None,
    foreign_keys: typing.Optional[list[typing.Any]] = None,
    lazy: str = "selectin",
    use_list: typing.Literal[True],
) -> list[EntityT]:
    ...


@typing.overload
def make_relation(
    relation: typing.Union[str, type[EntityT]],
    *,
    relation_name: str = "",
    back_populates: typing.Optional[str] = None,
    secondary: typing.Union[sa.Table, type, None] = None,
    foreign_keys: typing.Optional[list[typing.Any]] = None,
    lazy: str = "selectin",
    use_list: typing.Literal[False] = False,
) -> EntityT:
    ...


@typing.overload
def make_relation(
    relation: typing.Callable[[], type[EntityT]],
    *,
    relation_name: str = "",
    back_populates: typing.Optional[str] = None,
    secondary: typing.Union[sa.Table, type, None] = None,
    foreign_keys: typing.Optional[list[typing.Any]] = None,
    lazy: str = "selectin",
    use_list: typing.Literal[False] = False,
) -> EntityT:
    ...


@typing.overload
def make_relation(
    relation: typing.Callable[[], type[EntityT]],
    *,
    relation_name: str,
    back_populates: typing.Optional[str] = None,
    secondary: typing.Union[sa.Table, type, None] = None,
    foreign_keys: typing.Optional[list[typing.Any]] = None,
    lazy: str = "selectin",
    use_list: typing.Literal[True],  # pylint: disable=unused-argument
) -> list[EntityT]:
    ...


def make_relation(
    relation: typing.Union[
        str, type[EntityT], typing.Callable[[], type[EntityT]]
    ],
    *,
    relation_name: str = "",
    back_populates: typing.Optional[str] = None,
    secondary: typing.Union[sa.Table, type, None] = None,
    foreign_keys: typing.Optional[list[typing.Any]] = None,
    lazy: str = "selectin",
    use_list: bool = False,  # noqa
) -> typing.Union[EntityT, typing.Sequence[EntityT]]:
    rel_func = partial(
        relationship,
        back_populates=back_populates,
        lazy=lazy,
        secondary=secondary,
        foreign_keys=foreign_keys,
    )
    if isinstance(relation, str):
        return typing.cast(typing.Any, rel_func(argument=relation))
    if isinstance(relation, FunctionType):
        return typing.cast(typing.Any, rel_func(argument=relation_name))
    return typing.cast(typing.Any, rel_func(argument=relation.__qualname__))


def create_relation_table(table_name: str, *entities: str):
    return sa.Table(
        table_name,
        default_metadata,
        sa.Column("id", sa.Integer, primary_key=True),
        *[
            sa.Column(
                f"{entity}_id", sa.Integer, sa.ForeignKey(f"{entity}.id")
            )
            for entity in entities
        ],
    )
