import dataclasses
from typing import Any

from attrs import asdict
from attrs import define
from gyver.attrs import asdict as gasdict
from gyver.attrs import define as gdefine
from gyver.attrs.utils.functions import disassemble_type

from gyver import config
from gyver.config.adapter.attrs import AttrsResolverStrategy
from gyver.config.adapter.dataclass import DataclassResolverStrategy
from gyver.config.adapter.factory import AdapterConfigFactory
from gyver.config.adapter.gattrs import GyverAttrsResolverStrategy
from gyver.config.adapter.mark import as_config
from gyver.config.adapter.mark import mark
from gyver.config.adapter.pydantic import PydanticResolverStrategy
from gyver.database import DatabaseConfig
from gyver.database.utils import make_uri
from gyver.model import Model
from gyver.url import URL
from gyver.url import Netloc
from gyver.utils import json


@dataclasses.dataclass(frozen=True)
class PersonConfig:
    name: str
    emails: tuple[str, ...]
    counts: set[int]
    meta: dict[str, Any]


@mark
class AnotherConfig(Model):
    name: str
    emails: tuple[str, ...]
    counts: set[int]
    meta: dict[str, Any]


@define
class OtherConfig:
    name: str
    emails: tuple[str, ...]
    counts: set[int]
    meta: dict[str, Any]


@gdefine
class Another:
    name: str
    emails: tuple[str, ...]
    counts: set[int]
    meta: dict[str, Any]


factory = AdapterConfigFactory()


def test_adapter_factory_identifies_strategy_correctly():
    assert (
        factory.get_strategy_class(disassemble_type(PersonConfig))
        is DataclassResolverStrategy
    )
    assert (
        factory.get_strategy_class(disassemble_type(AnotherConfig))
        is PydanticResolverStrategy
    )
    assert (
        factory.get_strategy_class(disassemble_type(PersonConfig))
        is DataclassResolverStrategy
    )
    assert (
        factory.get_strategy_class(disassemble_type(AnotherConfig))
        is PydanticResolverStrategy
    )
    assert (
        factory.get_strategy_class(disassemble_type(OtherConfig))
        is AttrsResolverStrategy
    )
    assert (
        factory.get_strategy_class(disassemble_type(Another))
        is GyverAttrsResolverStrategy
    )


def test_adapter_parses_correctly_on_from_config():
    mapping = config.EnvMapping(
        {
            "NAME": "John Doe",
            "emails": "person@example.com,  john.doe@hi.com,doejohn@test.com",
            "COUNTS": "6,2, 7, 1",
        }
    )
    cfg = config.Config(mapping=mapping)
    factory = config.AdapterConfigFactory(cfg)
    presets = {"meta": {"spouse": "Jane Doe"}}

    person_config = factory.load(PersonConfig, presets=presets)
    another_config = factory.load(AnotherConfig, presets=presets)
    other_config = factory.load(OtherConfig, presets=presets)
    another = factory.load(Another, presets=presets)

    assert person_config.name == "John Doe"
    assert person_config.emails == (
        "person@example.com",
        "john.doe@hi.com",
        "doejohn@test.com",
    )
    assert person_config.counts == {6, 2, 7, 1}
    assert person_config.meta == {"spouse": "Jane Doe"}
    assert (
        dataclasses.asdict(person_config)
        == asdict(other_config)
        == another_config.dict()
        == gasdict(another)
    )


def test_adapter_uses_json_loads_if_receives_dict_as_param():
    mapping = config.EnvMapping(
        {
            "NAME": "John Doe",
            "emails": "person@example.com,  john.doe@hi.com,doejohn@test.com",
            "COUNTS": "6,2, 7, 1",
            "meta": json.dumps({"hello": "world"}),
        }
    )
    cfg = config.Config(mapping=mapping)
    factory = config.AdapterConfigFactory(cfg)
    person_config = factory.load(PersonConfig)
    assert person_config.meta == {"hello": "world"}


def test_boolean_cast_works_correctly():
    @as_config
    class CustomConfig:
        is_valid: bool

    assert (
        not config.AdapterConfigFactory(
            config.Config(mapping=config.EnvMapping({"IS_VALID": "False"}))
        )
        .load(CustomConfig)
        .is_valid
    )
    assert (
        not config.AdapterConfigFactory(
            config.Config(mapping=config.EnvMapping({"IS_VALID": "false"}))
        )
        .load(CustomConfig)
        .is_valid
    )
    assert (
        not config.AdapterConfigFactory(
            config.Config(mapping=config.EnvMapping({"IS_VALID": ""}))
        )
        .load(CustomConfig)
        .is_valid
    )
    assert (
        not config.AdapterConfigFactory(
            config.Config(mapping=config.EnvMapping({"IS_VALID": "0"}))
        )
        .load(CustomConfig)
        .is_valid
    )
    assert (
        not config.AdapterConfigFactory(
            config.Config(mapping=config.EnvMapping({"IS_VALID": "invalid"}))
        )
        .load(CustomConfig)
        .is_valid
    )
    assert (
        config.AdapterConfigFactory(
            config.Config(mapping=config.EnvMapping({"IS_VALID": "True"}))
        )
        .load(CustomConfig)
        .is_valid
    )
    assert (
        config.AdapterConfigFactory(
            config.Config(mapping=config.EnvMapping({"IS_VALID": "true"}))
        )
        .load(CustomConfig)
        .is_valid
    )
    assert (
        config.AdapterConfigFactory(
            config.Config(mapping=config.EnvMapping({"IS_VALID": "1"}))
        )
        .load(CustomConfig)
        .is_valid
    )


def test_old_config_works_with_adapter_factory():
    factory = config.AdapterConfigFactory(
        config.Config(
            mapping=config.EnvMapping(
                {
                    "DB_USER": "internal-api",
                    "DB_PASSWORD": "dummy-password",
                    "DB_NAME": "internal_api",
                    "DB_HOST": "localhost",
                    "DB_DRIVER": "postgres",
                }
            )
        )
    )

    cfg = factory.load(DatabaseConfig, "db")
    db_url = URL("")
    db_url.scheme = "postgresql+asyncpg"
    db_url.add(
        path="internal_api",
        netloc_obj=Netloc("").set(
            host="localhost",
            username="internal-api",
            password="dummy-password",
            port=5432,
        ),
    )
    assert make_uri(cfg) == db_url.encode()


def test_config_factory_support_for_nested_classes():
    @gdefine
    class Test:
        name: str

    @gdefine
    class Another:
        test: Test
        name: str

    cfg = config.Config(
        mapping=config.EnvMapping(
            {
                "NAME": "name",
                "TEST__NAME": "test_name",
                "ANOTHER_NAME": "another_name",
                "ANOTHER_TEST__NAME": "another_test_name",
            }
        )
    )

    factory = config.AdapterConfigFactory(cfg)

    assert factory.load(Another) == Another(Test("test_name"), "name")
    assert factory.load(Another, "another") == Another(
        Test("another_test_name"), "another_name"
    )
