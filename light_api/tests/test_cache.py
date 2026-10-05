"""Tests for light_api.cache."""

import base64
import dataclasses
import json
import os
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from cryptography.fernet import Fernet

from light_api import cache
from light_api.cache import CacheEntry, CacheModule


@pytest.fixture(autouse=True)
def isolated_cache_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "_cache_dir", lambda: str(tmp_path))
    return tmp_path


class TestSaveLoadRoundTrip:
    def test_round_trip_returns_same_data(self):
        data = {"a": 1, "b": [1, 2, 3]}
        cache.save(CacheModule.NOTES, "token-1", data)
        assert cache.load(CacheModule.NOTES, "token-1") == data

    def test_round_trip_scoped_by_key_is_independent_of_module_level_cache(self):
        cache.save(CacheModule.NOTES, "token-1", {"x": 1}, key="note-1")
        assert cache.load(CacheModule.NOTES, "token-1", key="note-1") == {"x": 1}
        assert cache.load(CacheModule.NOTES, "token-1") is None


class TestLoadMisses:
    def test_returns_none_when_file_missing(self):
        assert cache.load(CacheModule.NOTES, "token-1") is None

    def test_returns_none_when_expired(self, monkeypatch):
        cache.save(CacheModule.NOTES, "token-1", {"a": 1})
        future = time.time() + cache.CACHE_TTL_SECONDS + 1
        monkeypatch.setattr(cache.time, "time", lambda: future)
        assert cache.load(CacheModule.NOTES, "token-1") is None

    def test_returns_none_on_wrong_token(self):
        cache.save(CacheModule.NOTES, "token-1", {"a": 1})
        assert cache.load(CacheModule.NOTES, "token-2") is None

    def test_returns_none_on_corrupt_file(self, isolated_cache_dir):
        path = Path(cache._cache_path(CacheModule.NOTES))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("not json")

        assert cache.load(CacheModule.NOTES, "token-1") is None

    def test_returns_none_when_decrypted_payload_is_not_json(self, isolated_cache_dir):
        """A cache file that decrypts fine but holds non-JSON plaintext (e.g. a
        corrupted write) must be treated as a cache miss, not raise."""
        salt = os.urandom(16)
        fernet = Fernet(cache._derive_key("token-1", salt))
        entry = CacheEntry(
            cached_at=time.time(),
            salt=base64.urlsafe_b64encode(salt).decode(),
            encrypted_data=fernet.encrypt(b"not json").decode(),
        )
        path = Path(cache._cache_path(CacheModule.NOTES))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(dataclasses.asdict(entry)))

        assert cache.load(CacheModule.NOTES, "token-1") is None


class TestInvalidate:
    def test_removes_existing_cache_file(self):
        cache.save(CacheModule.NOTES, "t", {"a": 1})
        cache.invalidate(CacheModule.NOTES)
        assert cache.load(CacheModule.NOTES, "t") is None

    def test_no_error_when_nothing_cached(self):
        cache.invalidate(CacheModule.NOTES)  # should not raise

    def test_no_raise_on_oserror(self, monkeypatch):
        cache.save(CacheModule.NOTES, "t", {"a": 1})
        monkeypatch.setattr(
            cache.os, "remove", MagicMock(side_effect=PermissionError("nope"))
        )
        cache.invalidate(CacheModule.NOTES)  # should not raise, just logs


class TestClear:
    def test_returns_zero_when_cache_dir_missing(self, isolated_cache_dir, monkeypatch):
        nonexistent = isolated_cache_dir / "does-not-exist"
        monkeypatch.setattr(cache, "_cache_dir", lambda: str(nonexistent))
        assert cache.clear() == 0

    def test_removes_all_files_and_returns_count(self, isolated_cache_dir):
        cache.save(CacheModule.NOTES, "t", {"a": 1})
        cache.save(CacheModule.MUSIC, "t", {"b": 2}, key="track-1")

        removed = cache.clear()

        assert removed == 2
        assert not os.path.isdir(cache._cache_dir())


class TestSaveErrors:
    def test_no_raise_on_makedirs_failure(self, monkeypatch):
        monkeypatch.setattr(
            cache.os, "makedirs", MagicMock(side_effect=OSError("disk full"))
        )
        cache.save(CacheModule.NOTES, "t", {"a": 1})  # should not raise
        assert cache.load(CacheModule.NOTES, "t") is None

    def test_cleans_up_tmp_file_when_replace_fails(self, monkeypatch, isolated_cache_dir):
        monkeypatch.setattr(cache.os, "replace", MagicMock(side_effect=OSError("boom")))

        cache.save(CacheModule.NOTES, "t", {"a": 1})  # should not raise

        leftover = list(isolated_cache_dir.glob("**/.tmp-*"))
        assert leftover == []


class TestDeriveKey:
    def test_same_token_and_salt_gives_same_key(self):
        salt = b"x" * 16
        assert cache._derive_key("tok", salt) == cache._derive_key("tok", salt)

    def test_different_token_gives_different_key(self):
        salt = b"x" * 16
        assert cache._derive_key("tok1", salt) != cache._derive_key("tok2", salt)
