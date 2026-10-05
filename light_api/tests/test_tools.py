"""Tests for light_api.tools."""

import pytest
import respx
import httpx

from helpers import API, make_light


class TestGetToolsMultiDevice:
    @respx.mock
    def test_only_returns_tools_for_selected_device(self, f_devices_multi, f_tools):
        target = f_devices_multi["data"][1]["id"]
        respx.get(f"{API}/api/devices").mock(
            return_value=httpx.Response(200, json=f_devices_multi)
        )
        respx.get(f"{API}/api/tools").mock(return_value=httpx.Response(200, json=f_tools))

        light = make_light(device_id=target)
        tools = light.tools.get_tools()

        other_device_tool_ids = {
            item["id"]
            for item in f_devices_multi["included"]
            if item["type"] == "device_tools"
            and item["relationships"]["device"]["data"]["id"] != target
        }
        assert len(tools) > 0
        for t in tools:
            assert t.device_tool_id not in other_device_tool_ids

    @respx.mock
    def test_raises_when_ambiguous(self, f_devices_multi, f_tools):
        respx.get(f"{API}/api/devices").mock(
            return_value=httpx.Response(200, json=f_devices_multi)
        )
        respx.get(f"{API}/api/tools").mock(return_value=httpx.Response(200, json=f_tools))

        light = make_light()
        with pytest.raises(RuntimeError, match="Multiple devices found"):
            light.tools.get_tools()
