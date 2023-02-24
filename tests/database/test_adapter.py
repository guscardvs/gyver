import pytest
import sqlalchemy as sa

from gyver import database
from gyver.config import AdapterConfigFactory
from gyver.config import Config
from gyver.config import EnvMapping
from gyver.database.utils import make_uri


@pytest.fixture
def working_factory():
    mapping = {"DB_DRIVER": "sqlite", "DB_HOST": "/:memory:"}
    config = Config(mapping=EnvMapping(mapping))
    return AdapterConfigFactory(config)


@pytest.fixture
def db_config(working_factory: AdapterConfigFactory):
    return working_factory.load(database.DatabaseConfig, __prefix__="db")


def test_database_config_works_correctly_with_config(
    working_factory: AdapterConfigFactory,
):
    db_config = working_factory.load(database.DatabaseConfig, __prefix__="db")

    assert isinstance(
        db_config.dialect,
        type(database.drivers.resolve_driver(database.Driver.SQLITE)),
    )
    assert db_config.host == "/:memory:"
    assert make_uri(db_config, sync=True) == "sqlite:///:memory:"


def test_database_provider_starts_correctly_with_working_factory(
    db_config: database.DatabaseConfig,
):
    adapter = database.DatabaseAdapter(db_config)

    with adapter.context() as conn:
        result = conn.execute(sa.select(sa.text('"Hello World"')))
        assert result.scalar_one() == "Hello World"


async def test_async_provider_starts_correctyl_with_working_factory(
    db_config: database.DatabaseConfig,
):
    provider = database.DatabaseAdapter(db_config)

    async with provider.async_context() as conn:
        result = await conn.execute(sa.select(sa.text('"Hello World"')))
        assert result.scalar_one() == "Hello World"
