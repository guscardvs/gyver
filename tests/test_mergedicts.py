from collections import OrderedDict

import pytest

from gyver.utils import merge_dicts


def test_merge_dicts_no_conflict():
    left = {"a": 1, "b": 2}
    right = {"c": 3, "d": 4}
    expected = {"a": 1, "b": 2, "c": 3, "d": 4}
    assert merge_dicts(left, right, on_conflict="strict") == expected


def test_merge_dicts_conflict_left():
    left = {"a": 1, "b": 2}
    right = {"b": 3, "c": 4}
    expected = {"a": 1, "b": 2, "c": 4}
    assert merge_dicts(left, right, on_conflict="left") == expected


def test_merge_dicts_conflict_right():
    left = {"a": 1, "b": 2}
    right = {"b": 3, "c": 4}
    expected = {"a": 1, "b": 3, "c": 4}
    assert merge_dicts(left, right, on_conflict="right") == expected


def test_merge_dicts_nested_dicts():
    left = {"a": {"x": 1, "y": 2}, "b": 3}
    right = {"a": {"y": 3, "z": 4}, "c": 5}
    expected = {"a": {"x": 1, "y": 3, "z": 4}, "b": 3, "c": 5}
    assert merge_dicts(left, right, on_conflict="right") == expected


def test_merge_dicts_merge_sequences():
    left = {"a": [1, 2, 3]}
    right = {"a": [4, 5, 6]}
    expected = {"a": [1, 2, 3, 4, 5, 6]}
    assert merge_dicts(left, right, on_conflict="right") == expected


def test_merge_dicts_skip_sequences():
    left = {"a": [1, 2, 3]}
    right = {"a": [4, 5, 6]}
    expected = {"a": [4, 5, 6]}
    assert (
        merge_dicts(left, right, on_conflict="right", merge_sequences=False) == expected
    )


def test_merge_dicts_ordered_dict():
    left = OrderedDict([("a", 1), ("b", 2)])
    right = OrderedDict([("b", 3), ("c", 4)])
    expected = {"a": 1, "b": 2, "c": 4}
    assert merge_dicts(left, right, on_conflict="left") == expected


def test_merge_dicts_strict_conflict_strategy():
    left = {"a": 1}
    right = {"a": 2}
    with pytest.raises(ValueError):
        merge_dicts(left, right, on_conflict="strict")


def test_merge_dicts_strict_nested_conflict_strategy():
    left = {"a": {"x": 1}}
    right = {"a": {"x": 2}}
    with pytest.raises(ValueError):
        merge_dicts(left, right, on_conflict="strict")


def test_merge_dicts_empty_dict():
    left = {}
    right = {"a": 1}
    expected = {"a": 1}
    assert merge_dicts(left, right, on_conflict="right") == expected


def test_merge_dicts_empty_dicts():
    left = {}
    right = {}
    expected = {}
    assert merge_dicts(left, right, on_conflict="right") == expected
