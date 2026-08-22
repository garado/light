"""Persistent local user preferences for the Light CLI."""

import json
import os
from typing import Any

import platformdirs

_DEFAULTS: dict[str, Any] = {
    "cache_enabled": False,
}


def _settings_path() -> str:
    return os.path.join(platformdirs.user_config_dir("light-cli"), "settings.json")


def _load() -> dict[str, Any]:
    try:
        with open(_settings_path()) as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return dict(_DEFAULTS)
    return {**_DEFAULTS, **data}


def _save(data: dict[str, Any]) -> None:
    path = _settings_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f)


def get_cache_enabled() -> bool:
    """Whether local response caching is persistently enabled."""
    return bool(_load().get("cache_enabled", False))


def set_cache_enabled(enabled: bool) -> None:
    """Set whether local response caching should be enabled by default."""
    data = _load()
    data["cache_enabled"] = enabled
    _save(data)
