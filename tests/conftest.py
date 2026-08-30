"""Shared fixtures for light API tests."""

import json
import os
import pytest
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def pytest_addoption(parser):
    parser.addoption(
        "--live",
        action="store_true",
        default=False,
        help="run live API contract tests against the real Light cloud "
        "(needs real credentials; never runs in CI)",
    )
    parser.addoption(
        "--strict-extra",
        action="store_true",
        default=False,
        help="live contract: also fail on response fields the spec does not document",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "live: hits the real Light API; requires --live (or LIGHT_LIVE_CONTRACT=1) "
        "plus credentials",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--live") or os.environ.get("LIGHT_LIVE_CONTRACT"):
        return
    skip_live = pytest.mark.skip(reason="live API test - pass --live to run")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)


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
