import pathlib

import pytest

from gyver.future.utils import finder
from tests.core.utils.mock_module import base

ROOT = pathlib.Path(__file__).parent.parent
MOD_PATH = ROOT / "core" / "utils" / "mock_module"


def test_finder_by_instance_finds_only_instances_of_given_class():
    instance_finder = (
        finder.FinderBuilder().instance_of(base.Base).from_path(ROOT).build(MOD_PATH)
    )

    result = instance_finder.find()

    assert result
    assert all(isinstance(value, base.Base) for value in result.values())


def test_finder_by_class_finds_only_subclasses_of_given_class():
    class_finder = (
        finder.FinderBuilder().child_of(base.Base).from_path(ROOT).build(MOD_PATH)
    )

    result = class_finder.find()

    assert result
    assert all(issubclass(value, base.Base) for value in result.values())
    assert base.Base not in result.values()


def test_finder_fails_if_finder_receives_unexistant_root():
    root = pathlib.Path("invalid")
    builder = finder.FinderBuilder()

    with pytest.raises(ValueError) as exc_info:
        builder.from_path(root)

    assert str(exc_info.value) == str(
        finder.InvalidPath(f"root must be a valid path, received {root}")
    )


def test_builder_selects_correct_project_folder():
    builder = finder.FinderBuilder()
    builder.from_project()
    assert builder.root == ROOT.parent


def test_builder_selects_correct_package_folder():
    builder = finder.FinderBuilder()
    builder.from_package()
    assert builder.root == ROOT


def test_builder_works_correctly_without_setting_path():
    instance_finder = finder.builder.instance_of(base.Base).build(MOD_PATH)

    result = instance_finder.find()

    assert result
    assert all(isinstance(value, base.Base) for value in result.values())
