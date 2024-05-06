import dataclasses
from enum import Enum
from typing import Any, Literal, TypeAlias

import pytest
from attrs import asdict, define
from config import InvalidCast

from gyver import config
from gyver.attrs import asdict as gasdict
from gyver.attrs import define as gdefine
from gyver.attrs.utils.functions import disassemble_type
from gyver.config.adapter.attrs import AttrsResolverStrategy
from gyver.config.adapter.dataclass import DataclassResolverStrategy
from gyver.config.adapter.factory import AdapterConfigFactory
from gyver.config.adapter.gattrs import GyverAttrsResolverStrategy
from gyver.config.adapter.mark import as_config, mark
from gyver.config.adapter.pydantic import PydanticResolverStrategy
from gyver.model import Model, v1
from gyver.utils import json


@dataclasses.dataclass(frozen=True)
class PersonConfig:
    name: str
    emails: tuple[str, ...]
    counts: set[int]
    meta: dict[str, Any]
    account: Literal["admin", "user"]


@mark
class AnotherConfig(Model):
    name: str
    emails: tuple[str, ...]
    counts: set[int]
    meta: dict[str, Any]
    account: Literal["admin", "user"]


@mark
class AnotherV1Config(v1.Model):
    name: str
    emails: tuple[str, ...]
    counts: set[int]
    meta: dict[str, Any]
    account: Literal["admin", "user"]


@define
class OtherConfig:
    name: str
    emails: tuple[str, ...]
    counts: set[int]
    meta: dict[str, Any]
    account: Literal["admin", "user"]


@gdefine
class Another:
    name: str
    emails: tuple[str, ...]
    counts: set[int]
    meta: dict[str, Any]
    account: Literal["admin", "user"]


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
        factory.get_strategy_class(disassemble_type(AnotherV1Config))
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
            "ACCOUNT": "admin",
        }
    )
    cfg = config.Config(mapping=mapping)
    factory = config.AdapterConfigFactory(cfg)
    presets = {"meta": {"spouse": "Jane Doe"}}

    person_config = factory.load(PersonConfig, presets=presets)
    another_config = factory.load(AnotherConfig, presets=presets)
    another_v1_config = factory.load(AnotherV1Config, presets=presets)
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
        == another_v1_config.dict()
        == another_config.model_dump()
        == gasdict(another)
    )


def test_adapter_uses_json_loads_if_receives_dict_as_param():
    mapping = config.EnvMapping(
        {
            "NAME": "John Doe",
            "emails": "person@example.com,  john.doe@hi.com,doejohn@test.com",
            "COUNTS": "6,2, 7, 1",
            "meta": json.dumps({"hello": "world"}),
            "account": "user",
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


LiteralValue: TypeAlias = Literal["a", "b"]


def test_literal_cast_works_correctly():
    class Option(Enum):
        VALUE = "value"

    @as_config
    class Test:
        options: Literal[1, "Other", b"Another", Option.VALUE, False]

    @as_config
    class Defaults:
        value: LiteralValue = "b"

    assert (
        config.AdapterConfigFactory(
            config.Config(mapping=config.EnvMapping({"OPTIONS": "1"}))
        )
        .load(Test)
        .options
        == 1
    )
    assert (
        config.AdapterConfigFactory(
            config.Config(mapping=config.EnvMapping({"OPTIONS": "Other"}))
        )
        .load(Test)
        .options
        == "Other"
    )
    assert (
        config.AdapterConfigFactory(
            config.Config(mapping=config.EnvMapping({"OPTIONS": "Another"}))
        )
        .load(Test)
        .options
        == b"Another"
    )
    assert (
        config.AdapterConfigFactory(
            config.Config(mapping=config.EnvMapping({"OPTIONS": "value"}))
        )
        .load(Test)
        .options
        is Option.VALUE
    )
    assert (
        config.AdapterConfigFactory(
            config.Config(mapping=config.EnvMapping({"OPTIONS": "false"}))
        )
        .load(Test)
        .options
        is False
    )
    assert (
        config.AdapterConfigFactory(config.Config(mapping=config.EnvMapping({})))
        .load(Defaults)
        .value
        == "b"
    )

    with pytest.raises(InvalidCast):
        assert config.AdapterConfigFactory(
            config.Config(mapping=config.EnvMapping({"OPTIONS": "invalid"}))
        ).load(Test)


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


def test_parametrize_loads_parameters_as_expected():
    def mock_function(val1: str, val2: int, val3) -> tuple[str, int, Any]:
        return val1, val2, val3

    cfg = config.Config(
        mapping=config.EnvMapping({"VAL1": "example", "VAL2": "2", "VAL3": "False"})
    )

    result = config.parametrize(mock_function, __config__=cfg)
    assert result == ("example", 2, "False")


def test_parametrize_raises_warning_if_no_args_found():
    def mock_funca():
        pass

    def mock_funcb(a: int):
        return a

    with pytest.warns(UserWarning) as winfo:
        resulta = config.parametrize(mock_funca)
    assert (
        str(winfo.pop().message)
        == f"No args could be inspected in function: {mock_funca.__name__}"
    )
    with pytest.warns(UserWarning) as winfo:
        resultb = config.parametrize(mock_funcb, __kwargs_type__="presets", a=35)
    assert (
        str(winfo.pop().message)
        == f"No args could be inspected in function: {mock_funcb.__name__}"
    )

    assert resulta is None
    assert resultb == 35


def test_parametrize_transforms_key_correctly():
    def func(val: str) -> str:
        return val

    cfg = config.Config(mapping=config.EnvMapping({"val": "Hello", "VAL": "World"}))

    assert (
        f"{config.parametrize(func, __transform__=str, __config__=cfg)}, {config.parametrize(func, __transform__=str.upper, __config__=cfg)}"
        == "Hello, World"
    )


def test_parametrize_applies_defaults_properly():
    def test(greeting: str, name: str) -> str:
        return f"{greeting}, {name}"

    cfg = config.Config(mapping=config.EnvMapping({"NAME": "John Doe"}))

    assert (
        config.parametrize(
            test,
            __config__=cfg,
            __kwargs_type__="defaults",
            greeting="Hello",
            name="Jane Doe",
        )
        == "Hello, John Doe"
    )


def test_parametrize_supports_config_classes():
    @as_config
    class Person:
        name: str
        email: str
        age: int

    def say_hello(person: Person):
        return (
            f"Hello, I'm {person.name}. My email is {person.email}. I'm {person.age}."
        )

    cfg = config.Config(
        mapping=config.EnvMapping(
            {"PERSON_NAME": "John Doe", "PERSON_EMAIL": "johndoe@example.com"}
        )
    )

    assert (
        config.parametrize(say_hello, __config__=cfg, person_age=31)
        == "Hello, I'm John Doe. My email is johndoe@example.com. I'm 31."
    )


async def test_attribute_loader_loads_values_properly():
    cfg = config.Config(
        mapping=config.EnvMapping({"FACTOR": "3", "PREFIXED_FACTOR": "3.7"})
    )

    @gdefine
    class Test:
        initial_value: float

        @config.AttributeLoader(__config__=cfg).lazy
        def factora(self, factor: float) -> float:
            return self.initial_value * factor

        @config.AttributeLoader(__prefix__="prefixed", __config__=cfg).asynclazy
        async def factorb(self, factor: float) -> float:
            return self.initial_value * factor

    test = Test(3)

    assert test.factora == test.initial_value * 3
    assert await test.factorb() == test.initial_value * 3.7
