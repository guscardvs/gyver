from datetime import datetime
from datetime import timedelta
from datetime import timezone

import fakeredis._server as fakeredis
import pytest
from fakeredis import aioredis

from gyver.cache.config import CacheConfig
from gyver.cache.mapper import AsyncCacheMap
from gyver.cache.mapper import CacheMap
from gyver.cache.redis import AsyncRedisWrapper
from gyver.cache.redis import RedisWrapper
from gyver.exc import CacheMiss
from gyver.utils import lazyfield


def _make_cache_config():
    return CacheConfig(host="test")


def _make_cache_instance():
    new_cls = type(
        "FakeRedisWrapper",
        (RedisWrapper,),
        {"_instance": lazyfield(lambda _: fakeredis.FakeRedis())},
    )
    return new_cls(_make_cache_config())


async def _make_async_cache():
    new_cls = type(
        "FakeAsyncRedisWrapper",
        (AsyncRedisWrapper,),
        {"_instance": lazyfield(lambda _: aioredis.FakeRedis())},
    )
    instance = new_cls(_make_cache_config())
    await instance._instance.flushdb()
    return instance


def test_redis_wrapper_works_correctly():
    cache = _make_cache_instance()
    dt = datetime.now(timezone.utc) + timedelta(days=1)

    cache.set("val1", 1, -1)
    assert cache.get("val1") == 1

    cache.set("val2", 2, dt)
    assert cache.get("val2") == 2


def test_redis_wrapper_get_raises_error_correctly():
    cache = _make_cache_instance()
    with pytest.raises(CacheMiss):
        cache.get("name")


def test_redis_wrapper_works_correctly_with_mapper():
    mapper = CacheMap(_make_cache_instance(), "name")

    mapper.set("val1", 1)

    assert mapper.get("val1") == 1

    with pytest.raises(CacheMiss):
        mapper.get("val2")

    mapper.set("val2", {"user_id": 2})

    assert mapper.get("val2") == {"user_id": 2}


def test_redis_wrapper_deletes_correctly():

    cache = _make_cache_instance()
    mapper = CacheMap(cache, "name")
    mapper.set("val1", 1)
    cache.delete("val1", "name")

    with pytest.raises(CacheMiss):
        mapper.get("val1")

    cache.delete("name")

    with pytest.raises(CacheMiss):
        cache.get("name")


async def test_async_cache_works_correctly():
    expected = {"users": [1, 2, 3]}
    dt = datetime.now(timezone.utc) + timedelta(days=1)

    cache = await _make_async_cache()
    await cache.set("name", expected, dt)

    assert await cache.get("name") == expected


async def test_async_cache_raises_cache_miss_correctly():

    cache = await _make_async_cache()

    with pytest.raises(CacheMiss):
        result = await cache.get("name")
        print(result)


async def test_async_cache_works_properly_with_mapper():
    mapper = AsyncCacheMap(await _make_async_cache(), "name")
    await mapper.set("val1", 1)

    assert await mapper.get("val1") == 1

    with pytest.raises(CacheMiss):
        await mapper.get("val2")

    await mapper.set("val2", {"user_id": 2})

    assert await mapper.get("val2") == {"user_id": 2}


async def test_async_cache_deletes_correctly():
    cache = await _make_async_cache()
    mapper = AsyncCacheMap(cache, "name")
    await mapper.set("val1", 1)
    await cache.delete("val1", "name")

    with pytest.raises(CacheMiss):
        await mapper.get("val1")

    await cache.delete("name")

    with pytest.raises(CacheMiss):
        await cache.get("name")
