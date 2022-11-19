import pathlib

import pytest

from gyver.utils import finder

from .mock_module import base

ROOT = pathlib.Path(__file__).parent.parent.parent
MOD_PATH = ROOT / "core" / "utils" / "mock_module"


def test_finder_by_instance_finds_only_instances_of_given_class():
    instance_finder = finder.Finder(
        finder.instance_validator(base.Base), ROOT, MOD_PATH
    )
    instance_finder.find()
    result = instance_finder.output

    assert result
    assert all(isinstance(value, base.Base) for value in result.values())


def test_finder_by_class_finds_only_subclasses_of_given_class():
    class_finder = finder.Finder(
        finder.class_validator(base.Base), ROOT, MOD_PATH
    )
    class_finder.find()
    result = class_finder.output

    assert result
    assert all(issubclass(value, base.Base) for value in result.values())
    assert base.Base not in result.values()


def test_finder_fails_if_finder_receives_unexistant_root():
    root = pathlib.Path("invalid")

    with pytest.raises(ValueError) as exc_info:
        finder.Finder(lambda a: bool(a), root)

    assert str(exc_info.value) == str(
        finder.InvalidPath(f"root must be a valid path, received {root}")
    )
