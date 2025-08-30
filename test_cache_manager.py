import time
import pytest

from cache_manager import (
    MemoryCache,
    PersistentCache,
    CacheManager
)

@pytest.fixture
def memory_cache():
    return MemoryCache()

@pytest.fixture
def persistent_cache(tmp_path):
    db_file = tmp_path / "test_cache.db"
    return PersistentCache(str(db_file))

@pytest.fixture
def cache_manager_memory():
    return CacheManager(use_persistent=False)

@pytest.fixture
def cache_manager_persistent(tmp_path):
    db_file = tmp_path / "test_cache.db"
    return CacheManager(use_persistent=True, db_path=str(db_file))

# ==== MemoryCache Tests ====
def test_memorycache_set_get(memory_cache):
    memory_cache.set("a", 123)
    assert memory_cache.get("a") == 123
    assert memory_cache.exists("a")
    assert "a" in memory_cache.keys()
    assert memory_cache.size() == 1

def test_memorycache_delete_clear(memory_cache):
    memory_cache.set("a", 123)
    assert memory_cache.delete("a") is True
    assert memory_cache.get("a") is None
    assert memory_cache.delete("a") is False

    memory_cache.set("b", 456)
    memory_cache.clear()
    assert memory_cache.size() == 0

def test_memorycache_age_and_timestamp(memory_cache):
    memory_cache.set("a", "value")
    ts = memory_cache.get_timestamp("a")
    assert isinstance(ts, float)

    age = memory_cache.get_age("a")
    assert age >= 0

# ==== PersistentCache Tests ====
def test_persistentcache_set_get(persistent_cache):
    persistent_cache.set("x", {"foo": "bar"})
    val = persistent_cache.get("x")
    assert val == {"foo": "bar"}
    assert persistent_cache.exists("x")
    assert "x" in persistent_cache.keys()
    assert persistent_cache.size() == 1

def test_persistentcache_delete_clear(persistent_cache):
    persistent_cache.set("y", [1, 2, 3])
    assert persistent_cache.delete("y") is True
    assert persistent_cache.get("y") is None
    assert persistent_cache.delete("y") is False

    persistent_cache.set("z", "test")
    persistent_cache.clear()
    assert persistent_cache.size() == 0

def test_persistentcache_age_and_timestamp(persistent_cache):
    persistent_cache.set("a", "value")
    ts = persistent_cache.get_timestamp("a")
    assert isinstance(ts, float)

    age = persistent_cache.get_age("a")
    assert age >= 0

def test_persistentcache_cleanup_old_entries(persistent_cache):
    persistent_cache.set("old", "data")
    # Forzare created_at nel passato
    with persistent_cache._get_connection() as conn:
        conn.execute("UPDATE cache SET created_at = datetime('now', '-40 days') WHERE key = 'old'")
    removed = persistent_cache.cleanup_old_entries(days=30)
    assert removed == 1
    assert not persistent_cache.exists("old")

# ==== CacheManager (Memory + Persistent) ====
@pytest.mark.parametrize("cache_manager_fixture", ["cache_manager_memory", "cache_manager_persistent"])
def test_cachemanager_set_get(request, cache_manager_fixture):
    cache = request.getfixturevalue(cache_manager_fixture)
    cache.set("k1", 42)
    assert cache.get("k1") == 42
    assert cache.exists("k1")
    assert "k1" in cache.keys()
    assert cache.size() == 1

@pytest.mark.parametrize("cache_manager_fixture", ["cache_manager_memory", "cache_manager_persistent"])
def test_cachemanager_delete_and_clear(request, cache_manager_fixture):
    cache = request.getfixturevalue(cache_manager_fixture)
    cache.set("k2", "value")
    assert cache.delete("k2") is True
    assert cache.get("k2") is None
    cache.set("k3", "another")
    cache.clear()
    assert cache.size() == 0

@pytest.mark.parametrize("cache_manager_fixture", ["cache_manager_memory", "cache_manager_persistent"])
def test_cachemanager_get_or_set_and_ttl(request, cache_manager_fixture):
    cache = request.getfixturevalue(cache_manager_fixture)

    def factory():
        return "new_value"

    # Primo inserimento
    val = cache.get_or_set("computed", factory)
    assert val == "new_value"

    # Recupera dalla cache
    val2 = cache.get_or_set("computed", lambda: "other")
    assert val2 == "new_value"

    # TTL scaduto
    cache.set("temp", "abc")
    time.sleep(0.05)
    assert cache.is_expired("temp", ttl_seconds=0.01)

    # get_if_fresh
    assert cache.get_if_fresh("temp", ttl_seconds=100) == "abc"
    assert cache.get_if_fresh("temp", ttl_seconds=0.01) is None

    # get_or_set_if_stale
    val3 = cache.get_or_set_if_stale("temp", lambda: "refreshed", ttl_seconds=0.01)
    assert val3 == "refreshed"

    # cleanup_expired_keys
    cache.set("shortlived", "x")
    time.sleep(0.05)
    removed = cache.cleanup_expired_keys(0.01)
    assert removed >= 1