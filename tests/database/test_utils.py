import pytest

from gyver import database
from gyver.database.drivers.mysql import MysqlDialect
from gyver.exc import InvalidField


def test_make_uri_should_return_expected_uri():
    expected = "mysql+aiomysql://user:Pas%24word@localhost:3306/database_name"
    config = database.DefaultDatabaseConfig(
        driver=database.Driver.MYSQL,
        host="localhost",
        user="user",
        password="Pas$word",
        name="database_name",
    )

    assert database.make_uri(config, False) == expected


def test_make_uri_builds_correctly_with_custom_dialect():
    expected = "mariadb+asyncmy://user:Pas%24word@localhost:3306/database_name"

    class AsyncmyMariaDialect(MysqlDialect):
        async_driver = "asyncmy"
        dialect_name = "mariadb"

    config = database.DefaultDatabaseConfig(
        driver=database.Driver.CUSTOM,
        host="localhost",
        user="user",
        password="Pas$word",
        name="database_name",
    )
    config.override_dialect(AsyncmyMariaDialect())
    assert database.make_uri(config, False) == expected


def test_dialect_resolution_fails_if_custom_not_provided():

    config = database.DefaultDatabaseConfig(
        driver=database.Driver.CUSTOM,
        host="localhost",
        user="user",
        password="Pas$word",
        name="database_name",
    )
    with pytest.raises(InvalidField):
        config.dialect
