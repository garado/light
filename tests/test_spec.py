"""Tests for openapi-spec.json."""

import copy
import json
from pathlib import Path

import pytest

from open_api_specification_client.models.get_api_devices_response_200 import (
    GetApiDevicesResponse200,
)

SPEC_PATH = Path(__file__).parent.parent / "light_api" / "openapi-spec.json"

PATHS = {
    "device_tool_location.data": [
        "data",
        0,
        "relationships",
        "device_tool_location",
        "data",
    ],
    "sim.data": ["data", 0, "relationships", "sim", "data"],
    "address.state": ["included", 6, "attributes", "config", "address", "state"],
    "address.stateCode": [
        "included",
        6,
        "attributes",
        "config",
        "address",
        "stateCode",
    ],
    "address.county": ["included", 6, "attributes", "config", "address", "county"],
    "address.postalCode": [
        "included",
        6,
        "attributes",
        "config",
        "address",
        "postalCode",
    ],
    "address.city": ["included", 6, "attributes", "config", "address", "city"],
}


@pytest.fixture
def spec():
    return json.loads(SPEC_PATH.read_text())


def without_key(d: dict, path: list) -> dict:
    """Return a deep copy of d with the key at path (e.g. ["a", "b", "c"])
    removed from its parent dict."""
    d = copy.deepcopy(d)
    target = d
    for key in path[:-1]:
        target = target[key]
    del target[path[-1]]
    return d


def with_null(d: dict, path: list) -> dict:
    """Return a deep copy of d with the value at path set to None."""
    d = copy.deepcopy(d)
    target = d
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = None
    return d


class TestDevicesSpec:
    def test_device_tool_location_present_or_null(self, f_devices):
        """device_tool_location.data can be a real record or null."""
        GetApiDevicesResponse200.from_dict(f_devices)

        nulled = with_null(f_devices, PATHS["device_tool_location.data"])
        GetApiDevicesResponse200.from_dict(nulled)

    def test_sim_present_or_null(self, f_devices):
        """sim.data can be a real record or null."""
        GetApiDevicesResponse200.from_dict(f_devices)

        nulled = with_null(f_devices, PATHS["sim.data"])
        GetApiDevicesResponse200.from_dict(nulled)

    @pytest.mark.parametrize(
        "key",
        [
            "address.state",
            "address.stateCode",
            "address.county",
            "address.postalCode",
            "address.city",
        ],
    )
    def test_address_field_can_be_missing(self, f_devices, key):
        """Non-US addresses don't send every field (no state/county equivalent, etc)."""
        GetApiDevicesResponse200.from_dict(f_devices)

        missing = without_key(f_devices, PATHS[key])
        GetApiDevicesResponse200.from_dict(missing)
