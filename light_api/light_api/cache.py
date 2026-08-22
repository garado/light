"""Local disk cache for API data, encrypted at rest with a key derived from the
current session's OAuth token.

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
import time
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

import platformdirs
from cryptography.fernet import Fernet, InvalidToken

log = logging.getLogger(f"light.{__name__}")

CACHE_TTL_SECONDS = 15 * 60


class CacheModule(StrEnum):
    """Modules with their own cache file."""

    PODCASTS = "podcasts"
    # NOTES = "notes"
    # MUSIC = "music"
    # TOOLS = "tools"
    # DEVICES = "devices"


@dataclass
class CacheEntry:
    """A module's cache file."""

    cached_at: float  # plaintext
    encrypted_data: str  # fernet token


def _cache_dir() -> str:
    return platformdirs.user_cache_dir("light-api-cli-tui")


def _cache_path(module: CacheModule) -> str:
    return os.path.join(_cache_dir(), f"{module}.json")


def _derive_key(token: str) -> bytes:
    """Derive a Fernet key from the session token via SHA-256."""
    digest = hashlib.sha256(token.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def load(module: CacheModule, token: str) -> Any | None:
    """Load cached data for `module` if it is present, unexpired, and decryptable.

    Returns None on any failure (missing file, expired, corrupt, wrong/stale token).
    """
    try:
        with open(_cache_path(module), "rb") as f:
            entry = CacheEntry(**json.loads(f.read()))
    except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError):
        return None

    if time.time() - entry.cached_at > CACHE_TTL_SECONDS:
        log.debug(f"Cache for {module!r} expired")
        return None

    try:
        fernet = Fernet(_derive_key(token))
        plaintext = fernet.decrypt(entry.encrypted_data.encode())
    except InvalidToken:
        log.debug(f"Cache for {module!r} undecryptable (stale/rotated token)")
        return None

    try:
        return json.loads(plaintext)
    except json.JSONDecodeError:
        return None


def save(module: CacheModule, token: str, data: Any) -> None:
    """Encrypt and cache `data` for `module`."""
    path = _cache_path(module)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    fernet = Fernet(_derive_key(token))
    encrypted = fernet.encrypt(json.dumps(data).encode()).decode()
    entry = CacheEntry(cached_at=time.time(), encrypted_data=encrypted)
    payload = json.dumps(dataclasses.asdict(entry))

    # create file with restrictive permissions
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(payload)


def invalidate(module: CacheModule) -> None:
    """Delete the cache file for `module`, if any."""
    try:
        os.remove(_cache_path(module))
    except FileNotFoundError:
        pass
