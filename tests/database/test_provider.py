import pytest
import sqlalchemy as sa

from gyver import database
from gyver.config import Config
from gyver.config import ConfigLoader
from gyver.config import EnvMapping
from gyver.database.utils import make_uri


@pytest.fixture
def working_config():
    mapping = {"DB_DRIVER": "sqlite", "DB_HOST": "/:memory:"}
    return Config(mapping=EnvMapping(mapping))


@pytest.fixture
def db_config(working_config: Config):
    return ConfigLoader(working_config, "db").load(database.DatabaseConfig)


def test_database_config_works_correctly_with_config(working_config: Config):
    db_config = ConfigLoader(working_config, prefix="db").load(database.DatabaseConfig)

    assert isinstance(
        db_config.dialect,
        type(database.drivers.resolve_driver(database.Driver.SQLITE)),
    )
    assert db_config.host == "/:memory:"
    assert make_uri(db_config, sync=True) == "sqlite:///:memory:"


def test_database_provider_starts_correctly_with_working_config(
    db_config: database.DatabaseConfig,
):
    provider = database.SyncDatabaseProvider(db_config)

    context = provider.context()

    with context.begin() as conn:
        result = conn.execute(sa.select(sa.text('"Hello World"')))
        assert result.scalar_one() == "Hello World"


async def test_async_provider_starts_correctyl_with_working_config(
    db_config: database.DatabaseConfig,
):
    provider = database.AsyncDatabaseProvider(db_config)

    context = provider.context()
    async with context.begin() as conn:
        result = await conn.execute(sa.select(sa.text('"Hello World"')))
        assert result.scalar_one() == "Hello World"
