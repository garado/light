"""Shared fixtures for light API tests."""

import json
import pytest
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def load(name: str) -> dict:
    return json.loads((FIXTURES / f"{name}.json").read_text())


@pytest.fixture
def f_devices():
    return load("devices")


@pytest.fixture
def f_devices_multi():
    return load("devices_multi")


@pytest.fixture
def f_devices_no_sim():
    return load("devices_no_sim")


@pytest.fixture
def f_tools():
    return load("tools")


@pytest.fixture
def f_notes():
    return load("notes")


@pytest.fixture
def f_playlist_items():
    return load("playlist_items")
