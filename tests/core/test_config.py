import tempfile
from pathlib import Path
from typing import Any

import pytest
from hypothesis import given
from hypothesis.strategies import text

from gyver import config
from gyver.config.adapter.mark import as_config
from gyver.exc import InvalidCast
from gyver.exc import MissingName


@given(text(), text())
def test_config_call_success(key: str, value: str):
    """test config call returns valid string
    from mapping source when name exists"""
    mapping = config.EnvMapping({key: value})
    cfg = config.Config(mapping=mapping)

    val = cfg(key)

    assert isinstance(val, str)
    assert val == value


def test_config_call_name_not_found():
    """test config call raises `config.MissingName`
    if name does not exists in source mapping"""
    mapping = config.EnvMapping({})
    cfg = config.Config(mapping=mapping)

    with pytest.raises(MissingName):
        cfg("invalid")


def test_config_cast_returns_cast_type():
    """test config cast returns cast type
    when name exists"""

    class _Cast:
        def __init__(self, val: str) -> None:
            self.val = val

    key = "key"
    value = "val"
    mapping = config.EnvMapping({key: value})
    cfg = config.Config(mapping=mapping)

    casted = cfg(key, _Cast)

    assert isinstance(casted, _Cast)
    assert casted.val == value


def test_config_cast_fails_with_invalid_cast():
    """test config cast fails with invalid cast
    when cast raises TypeError or ValueError"""

    def _fail_cast(val: str):
        raise TypeError

    mapping = config.EnvMapping({"key": "value"})
    cfg = config.Config(mapping=mapping)

    with pytest.raises(InvalidCast):
        cfg("key", _fail_cast)


def test_env_mapping_raises_errors_correctly_on_read():
    mapping = config.EnvMapping({})
    mapping["my-name"] = "val"
    mapping["my-name"]

    with pytest.raises(KeyError):
        mapping["my-name"] = "error"
    with pytest.raises(KeyError):
        del mapping["my-name"]


def test_config_reads_from_env_file():
    filename = tempfile.mktemp()
    with open(filename, "w") as buf:
        buf.write("HELLO=world\n")
        buf.write("# EMAIL=error\n")
    cfg = config.Config(filename)
    assert cfg("HELLO") == "world"

    with pytest.raises(MissingName):
        cfg("EMAIL")


@as_config
class PersonConfig:
    name: str
    emails: tuple[str, ...]
    counts: set[int]
    meta: dict[str, Any]


def test_provider_parses_correctly_on_from_config():
    mapping = config.EnvMapping(
        {
            "NAME": "John Doe",
            "emails": "person@example.com,  john.doe@hi.com,doejohn@test.com",
            "COUNTS": "6,2, 7, 1",
        }
    )
    cfg = config.Config(mapping=mapping)
    factory = config.AdapterConfigFactory(cfg)

    person_config = factory.load(PersonConfig, presets={"meta": {"spouse": "Jane Doe"}})

    assert person_config.name == "John Doe"
    assert person_config.emails == (
        "person@example.com",
        "john.doe@hi.com",
        "doejohn@test.com",
    )
    assert person_config.counts == {6, 2, 7, 1}
    assert person_config.meta == {"spouse": "Jane Doe"}


def test_envconfig_identifies_correct_layer_of_dotfile():
    mapping = config.EnvMapping({"CONFIG_ENV": "local"})
    curdir = Path(__file__).parent
    env_config = config.EnvConfig(
        config.DotFile(curdir / "test.env", config.Env.TEST), mapping=mapping
    )
    second_envconfig = config.EnvConfig(
        config.DotFile(curdir / "local.env", config.Env.LOCAL), mapping=mapping
    )
    third_envconfig = config.EnvConfig(
        config.DotFile(curdir / "test.env", config.Env.TEST, apply_to_lower=True),
        config.DotFile(curdir / "local.env", config.Env.LOCAL),
        mapping=mapping,
    )
    assert env_config.dotfile is None
    assert second_envconfig.dotfile and second_envconfig.dotfile.env is config.Env.LOCAL
    assert third_envconfig.dotfile and third_envconfig.dotfile.env is config.Env.TEST


def test_envconfig_ignores_dotfiles_without_valid_files():
    mapping = config.EnvMapping({"CONFIG_ENV": "local"})
    env_config = config.EnvConfig(
        config.DotFile("invalid", config.Env.LOCAL), mapping=mapping
    )

    assert env_config.dotfile is None
