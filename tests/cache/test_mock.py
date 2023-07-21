from datetime import datetime
from datetime import timedelta
from datetime import timezone

import pytest

from gyver.cache.mapper import AsyncCacheMap
from gyver.cache.mapper import CacheMap
from gyver.cache.mock import MockAsyncCache
from gyver.cache.mock import MockCache
from gyver.cache.mock import _KeyMapType
from gyver.exc import CacheMiss
from gyver.utils import json


def test_mock_cache_sets_correctly_values():
    mapping = {}
    cache = MockCache(mapping)
    dt = datetime.now(timezone.utc) + timedelta(days=1)
    cache.set("val1", 1, -1)
    cache.set("val2", 2, dt)

    assert mapping["val1"] == ("1", None)
    assert mapping["val2"] == ("2", dt)


def test_mock_cache_gets_correctly_values():
    dt = datetime.now(timezone.utc) + timedelta(days=1)
    mapping: _KeyMapType = {"name": ('{"user_id": 2}', dt)}
    cache = MockCache(mapping)

    assert cache.get("name") == {"user_id": 2}


def test_mock_cache_get_raises_error_on_expiration_correctly():
    dt = datetime.now(timezone.utc) - timedelta(days=1)
    mapping: _KeyMapType = {"name": (json.dumps({"user_id": 2}), dt)}
    cache = MockCache(mapping)

    with pytest.raises(CacheMiss):
        cache.get("name")


def test_mock_cache_works_correctly_with_mapper():
    mapping: _KeyMapType = {"name": {"val1": "1"}}
    mapper = CacheMap(MockCache(mapping), "name")

    assert mapper.get("val1") == 1

    with pytest.raises(CacheMiss):
        mapper.get("val2")

    mapper.set("val2", {"user_id": 2})

    assert mapper.get("val2") == {"user_id": 2}


def test_mock_cache_deletes_correctly():
    mapping = {"name": {"val1": "1"}, "val2": "2"}

    cache = MockCache(mapping)

    cache.delete("val1", "name")

    assert "name" in mapping and not mapping["name"]

    cache.delete("name")

    with pytest.raises(KeyError):
        mapping["name"]

    mapper = CacheMap(cache, "name")
    with pytest.raises(CacheMiss):
        mapper.get("val1")


async def test_async_mock_gets_correctly():
    expected = {"users": [1, 2, 3]}
    dt = datetime.now(timezone.utc) + timedelta(days=1)
    mapping = {"name": (json.dumps(expected), dt)}

    cache = MockAsyncCache(mapping)

    assert await cache.get("name") == expected


async def test_async_mock_sets_correctly():
    mapping = {}

    cache = MockAsyncCache(mapping)

    await cache.set("name", 1, -1)

    assert await cache.get("name") == 1


async def test_async_mock_raises_cache_miss_correctly():
    mapping = {}

    cache = MockAsyncCache(mapping)

    with pytest.raises(CacheMiss):
        await cache.get("name")


async def test_async_mock_works_properly_with_mapper():
    mapping = {"name": {"val1": "1"}}
    mapper = AsyncCacheMap(MockAsyncCache(mapping), "name")

    assert await mapper.get("val1") == 1

    with pytest.raises(CacheMiss):
        await mapper.get("val2")

    await mapper.set("val2", {"user_id": 2})

    assert await mapper.get("val2") == {"user_id": 2}


async def test_async_mock_deletes_correctly():
    mapping = {"name": {"val1": "1"}, "val2": "2"}

    cache = MockAsyncCache(mapping)

    await cache.delete("val1", "name")

    assert "name" in mapping and not mapping["name"]

    await cache.delete("name")

    with pytest.raises(KeyError):
        mapping["name"]

    mapper = AsyncCacheMap(cache, "name")
    with pytest.raises(CacheMiss):
        await mapper.get("val1")
