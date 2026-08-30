"""Local disk cache for API data.

Each cache file is encrypted with a key derived (scrypt + per-file salt)
from the current session token. This protects cache copies that get separated
from your OS keyring - backups, synced folders, stray file permissions - and
guarantees that a cache from an old session can't be read.

It is NOT a defense against code running as your user, which can read the session
token directly.

- Cache is off by default. It can be enabled with a CLI command.
    - The cache setting for each command invocation is overridable at these priority levels:
        - CLI flag > env var > cached persistent setting > default (off).
- Each module (notes/music/etc) gets its own cache file
- Cached data is valid for CACHE_TTL_SECONDS (15min by default)
- Mutative operations invalidate its respective module's cache
"""

import base64
import dataclasses
import hashlib
import json
import logging
import os
import shutil
import tempfile
import time
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

import platformdirs
from cryptography.fernet import Fernet, InvalidToken

log = logging.getLogger(f"light.{__name__}")

CACHE_TTL_SECONDS = 15 * 60

# scrypt cost parameters
_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1
_SCRYPT_MAXMEM = 64 * 1024 * 1024
_SALT_BYTES = 16


class CacheModule(StrEnum):
    """Modules with their own cache file(s)."""

    PODCASTS = "podcasts"
    NOTES = "notes"
    MUSIC = "music"
    TOOLS = "tools"
    DEVICES = "devices"


@dataclass
class CacheEntry:
    """A module's cache file."""

    cached_at: float  # plaintext
    salt: str  # plaintext, base64 - scrypt salt for encrypted_data's key
    encrypted_data: str  # fernet token


def _cache_dir() -> str:
    return platformdirs.user_cache_dir("light-api-cli-tui")


def _cache_path(module: CacheModule, key: str | None = None) -> str:
    """Path for a module's (or an item within a module's) cache file.

    `key=None` represents the entire module (e.g. cached `notes list`).
    Providing a key scopes the cachefile to an individual item (e.g. a specific note)
    under a per-module subdirectory.
    """
    if key is None:
        return os.path.join(_cache_dir(), f"{module}.json")
    return os.path.join(_cache_dir(), str(module), f"{key}.json")


def _label(module: CacheModule, key: str | None) -> str:
    return f"{module!r}" if key is None else f"{module!r}/{key!r}"


def _derive_key(token: str, salt: bytes) -> bytes:
    """Derive a Fernet key from the session token + salt via scrypt."""
    digest = hashlib.scrypt(
        token.encode(),
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        maxmem=_SCRYPT_MAXMEM,
        dklen=32,
    )
    return base64.urlsafe_b64encode(digest)


def load(module: CacheModule, token: str, key: str | None = None) -> Any | None:
    """Load cached data for `module` (optionally scoped to `key`) if it is
    present, unexpired, and decryptable.

    Returns None on any failure (missing file, expired, corrupt, wrong/stale token).
    """
    label = _label(module, key)
    try:
        with open(_cache_path(module, key), "rb") as f:
            entry = CacheEntry(**json.loads(f.read()))
    except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError):
        log.debug(f"Cache for {label} missing")
        return None

    if time.time() - entry.cached_at > CACHE_TTL_SECONDS:
        log.debug(f"Cache for {label} expired")
        return None

    try:
        salt = base64.urlsafe_b64decode(entry.salt.encode())
        fernet = Fernet(_derive_key(token, salt))
        plaintext = fernet.decrypt(entry.encrypted_data.encode())
    except (InvalidToken, ValueError):
        log.debug(f"Cache for {label} undecryptable (stale/rotated token)")
        return None

    try:
        result = json.loads(plaintext)
    except json.JSONDecodeError:
        log.debug(f"Cache for {label} corrupt (bad JSON after decrypt)")
        return None

    log.debug(f"Cache for {label} hit")
    return result


def save(module: CacheModule, token: str, data: Any, key: str | None = None) -> None:
    """Encrypt and cache `data` for `module` (optionally scoped to `key`)."""
    path = _cache_path(module, key)
    cache_dir = os.path.dirname(path)

    salt = os.urandom(_SALT_BYTES)
    fernet = Fernet(_derive_key(token, salt))
    encrypted = fernet.encrypt(json.dumps(data).encode()).decode()
    entry = CacheEntry(
        cached_at=time.time(),
        salt=base64.urlsafe_b64encode(salt).decode(),
        encrypted_data=encrypted,
    )
    payload = json.dumps(dataclasses.asdict(entry))

    try:
        os.makedirs(cache_dir, exist_ok=True)

        # to avoid concurrent access issues: write to a tmp file, then atomically replace
        tmp_fd, tmp_path = tempfile.mkstemp(
            dir=cache_dir, prefix=".tmp-", suffix=".json"
        )
        try:
            with os.fdopen(tmp_fd, "w") as f:
                f.write(payload)
            os.replace(tmp_path, path)
        except BaseException:
            try:
                os.remove(tmp_path)
            except FileNotFoundError:
                pass
            raise
    except OSError as e:
        log.warning(f"Cache for {_label(module, key)} could not be saved: {e}")
        return

    log.debug(f"Cache for {_label(module, key)} saved")


def invalidate(module: CacheModule, key: str | None = None) -> None:
    """Delete the cache file for `module` (optionally scoped to `key`), if any."""
    try:
        os.remove(_cache_path(module, key))
    except FileNotFoundError:
        pass
    except OSError as e:
        log.warning(f"Cache for {_label(module, key)} could not be invalidated: {e}")


def clear() -> int:
    """Delete the entire local response cache. Returns the number of files removed."""
    root = _cache_dir()
    if not os.path.isdir(root):
        return 0
    removed = sum(len(files) for _, _, files in os.walk(root))
    shutil.rmtree(root, ignore_errors=True)
    log.debug(f"Cleared {removed} cache file(s) from {root}")
    return removed
