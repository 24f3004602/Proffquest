import json
import types
import builtins
import importlib
import time
import pytest


class FakeRedis:
    def __init__(self):
        self.store = {}
        self.deleted = []
        self._info = {
            'connected_clients': 1,
            'used_memory_human': '1M',
            'keyspace_hits': 0,
            'keyspace_misses': 0,
        }

    # Compatibility helpers
    @classmethod
    def from_url(cls, url, decode_responses=True):
        return cls()

    def ping(self):
        return True

    # Basic KV
    def get(self, key):
        value = self.store.get(key)
        if value is None:
            self._info['keyspace_misses'] = self._info.get('keyspace_misses', 0) + 1
        else:
            self._info['keyspace_hits'] = self._info.get('keyspace_hits', 0) + 1
        return value

    def setex(self, key, ttl, value):
        # We don't implement TTL expiry for tests
        self.store[key] = value
        return True

    def keys(self, pattern):
        # Very naive glob emulation: treat trailing * as prefix match
        if pattern.endswith('*'):
            prefix = pattern[:-1]
            return [k for k in self.store.keys() if k.startswith(prefix)]
        return [k for k in self.store.keys() if k == pattern]

    def delete(self, *keys):
        for k in keys:
            self.deleted.append(k)
            if k in self.store:
                del self.store[k]
        return len(keys)

    def info(self):
        # Include total keys count indirectly through tests
        return dict(self._info)


class FakeRedisError(Exception):
    pass


@pytest.fixture(autouse=True)
def ensure_clean_import(monkeypatch):
    # Provide a stub redis module so backend.utils.cache can import safely
    fake_redis_module = types.SimpleNamespace(
        from_url=FakeRedis.from_url,
        RedisError=FakeRedisError,
        ConnectionError=FakeRedisError,
    )
    monkeypatch.setitem(builtins.__dict__, '__test_fake_redis__', FakeRedis)  # debug aid if needed

    # If module already imported in a previous test run, remove it to re-evaluate REDIS_AVAILABLE
    for mod in list(importlib.sys.modules.keys()):
        if mod in ('backend.utils.cache',):
            del importlib.sys.modules[mod]

    monkeypatch.setitem(importlib.sys.modules, 'redis', fake_redis_module)


def import_cache_with(monkeypatch, redis_available=True):
    """Import backend.utils.cache with controllable REDIS availability.

    By default, FakeRedis.ping() succeeds so REDIS_AVAILABLE=True.
    To simulate unavailable, we override from_url to raise.
    """
    if not redis_available:
        fake_unavailable = types.SimpleNamespace(
            from_url=lambda *a, **k: (_ for _ in ()).throw(FakeRedisError('unavailable')),
            RedisError=FakeRedisError,
            ConnectionError=FakeRedisError,
        )
        monkeypatch.setitem(importlib.sys.modules, 'redis', fake_unavailable)
    cache = importlib.import_module('backend.utils.cache')
    return cache


def test_cache_response_caches_plain_result_with_key_builder(monkeypatch):
    cache = import_cache_with(monkeypatch, redis_available=True)

    calls = {'count': 0}

    @cache.cache_response(prefix=cache.CACHE_PREFIXES['analytics'], ttl_type='short', key_builder=lambda: 'fixed:key')
    def compute():
        calls['count'] += 1
        return {'value': 42}

    # First call executes function and caches
    r1 = compute()
    assert r1 == {'value': 42}
    assert calls['count'] == 1

    # Second call hits cache (no additional function call)
    r2 = compute()
    assert r2 == {'value': 42}
    assert calls['count'] == 1


def test_cache_response_tuple_200_caches_only_data(monkeypatch):
    cache = import_cache_with(monkeypatch, redis_available=True)

    calls = {'count': 0}

    @cache.cache_response(prefix=cache.CACHE_PREFIXES['drives'], key_builder=lambda: 'tuple:key')
    def endpoint():
        calls['count'] += 1
        return ({'items': [1, 2]}, 200)

    # Miss -> returns tuple
    data, status = endpoint()
    assert status == 200
    assert data == {'items': [1, 2]}
    assert calls['count'] == 1

    # Hit -> returns cached JSON (data only, not tuple)
    cached = endpoint()
    assert cached == {'items': [1, 2]}
    assert calls['count'] == 1


def test_cache_response_tuple_non_200_is_not_cached(monkeypatch):
    cache = import_cache_with(monkeypatch, redis_available=True)

    calls = {'count': 0}

    @cache.cache_response(prefix=cache.CACHE_PREFIXES['drives'], key_builder=lambda: 'tuple:non200')
    def endpoint_err():
        calls['count'] += 1
        return ({'error': 'bad'}, 400)

    r1 = endpoint_err()
    assert r1 == ({'error': 'bad'}, 400)
    assert calls['count'] == 1

    # Should not be cached; function called again
    r2 = endpoint_err()
    assert r2 == ({'error': 'bad'}, 400)
    assert calls['count'] == 2


def test_cache_response_falls_back_when_redis_unavailable(monkeypatch):
    cache = import_cache_with(monkeypatch, redis_available=False)

    calls = {'count': 0}

    @cache.cache_response(prefix=cache.CACHE_PREFIXES['students'], key_builder=lambda: 'k')
    def fn():
        calls['count'] += 1
        return {'ok': True}

    # Without Redis, both calls execute function
    assert fn() == {'ok': True}
    assert fn() == {'ok': True}
    assert calls['count'] == 2


def test_invalidate_cache_deletes_matching_keys(monkeypatch):
    cache = import_cache_with(monkeypatch, redis_available=True)

    # Prime some keys in the fake Redis
    # Access underlying client via module attribute
    client = cache.redis_client
    client.setex('pq:drives:a', 60, json.dumps(1))
    client.setex('pq:drives:b', 60, json.dumps(2))
    client.setex('pq:students:x', 60, json.dumps(3))

    # Invalidate drives only
    cache.invalidate_cache(['pq:drives:*'])

    # Ensure drives keys are deleted but students remain
    assert 'pq:drives:a' not in client.store
    assert 'pq:drives:b' not in client.store
    assert 'pq:students:x' in client.store


def test_get_cached_value_and_set_cached_value(monkeypatch):
    cache = import_cache_with(monkeypatch, redis_available=True)

    key = 'k1'
    assert cache.get_cached_value(key) is None

    ok = cache.set_cached_value(key, {'x': 1}, ttl_type='long')
    assert ok is True
    assert cache.get_cached_value(key) == {'x': 1}


def test_get_cache_stats_reports_keys_and_availability(monkeypatch):
    cache = import_cache_with(monkeypatch, redis_available=True)

    # Seed a few keys across prefixes
    client = cache.redis_client
    client.setex(f"{cache.CACHE_PREFIXES['companies']}:1", 60, json.dumps({'a': 1}))
    client.setex(f"{cache.CACHE_PREFIXES['analytics']}:stats", 60, json.dumps({'b': 2}))

    stats = cache.get_cache_stats()
    assert stats['available'] is True
    assert 'connected_clients' in stats
    assert stats['total_keys'] >= 2
    assert stats['keys_by_prefix']['companies'] >= 1
    assert stats['keys_by_prefix']['analytics'] >= 1
