"""Installed tools introspection for Light devices."""

import logging
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from light_api.client import Light

log = logging.getLogger(f"light.{__name__}")


class ToolName(StrEnum):
    ALARM = "alarm"
    ALBUM = "album"
    CALCULATOR = "calculator"
    CALENDAR = "calendar"
    CAMERA = "camera"
    DIRECTIONS = "directions"
    DIRECTORY = "directory"
    HOTSPOT = "hotspot"
    MUSIC = "music"
    NOTES = "notes"
    PODCASTS = "podcasts"
    TIMER = "timer"


@dataclass
class LightTool:
    device_tool_id: str
    global_tool_id: str
    namespace: str
    component: str
    title: str


class LightTools:
    def __init__(self, light: "Light") -> None:
        self._l = light

    def get_tools(self) -> list[LightTool]:
        """Return all tools installed on the device."""
        from open_api_specification_client.api.default import (
            get_api_devices,
            get_api_tools,
        )
        from open_api_specification_client.types import Unset

        devices_resp = self._l.call_api(
            get_api_devices.sync_detailed, client=self._l._api_client
        )

        if (
            devices_resp.status_code != 200
            or not devices_resp.parsed
            or not devices_resp.parsed.data
        ):
            raise RuntimeError(f"Could not fetch devices: {devices_resp.status_code}")

        device_id = self._l._select_device_id(devices_resp.parsed)

        tools_resp = get_api_tools.sync_detailed(
            client=self._l._api_client, device_id=device_id
        )

        if tools_resp.status_code != 200 or not tools_resp.parsed:
            raise RuntimeError(f"Could not fetch tools: {tools_resp.status_code}")

        tool_info = {
            t.id: (t.attributes.namespace, t.attributes.component, t.attributes.title)
            for t in tools_resp.parsed.data
        }

        results = []
        for item in devices_resp.parsed.included:
            if isinstance(item.relationships, Unset) or isinstance(
                item.relationships.tool, Unset
            ):
                continue
            if item.relationships.device.data.id != device_id:
                continue
            global_tool_id = item.relationships.tool.data.id
            ns, comp, title = tool_info.get(global_tool_id, ("", "", ""))
            results.append(
                LightTool(
                    device_tool_id=item.id,
                    global_tool_id=global_tool_id,
                    namespace=ns,
                    component=comp,
                    title=title,
                )
            )

        return sorted(results, key=lambda t: t.title.lower())

    def _get_device_id(self) -> str:
        from open_api_specification_client.api.default import get_api_devices
        resp = self._l.call_api(get_api_devices.sync_detailed, client=self._l._api_client)
        if resp.status_code != 200 or not resp.parsed or not resp.parsed.data:
            raise RuntimeError(f"Could not fetch devices: {resp.status_code}")
        return self._l._select_device_id(resp.parsed)

    def _resolve_global_tool_id(self, name: str) -> tuple[str, str]:
        """Return (global_tool_id, title) for a tool matching name (case-insensitive)."""
        from open_api_specification_client.api.default import get_api_tools
        device_id = self._get_device_id()
        resp = get_api_tools.sync_detailed(client=self._l._api_client, device_id=device_id)
        if resp.status_code != 200 or not resp.parsed:
            raise RuntimeError(f"Could not fetch tools: {resp.status_code}")
        needle = name.lower()
        matches = [
            t for t in resp.parsed.data
            if needle in t.attributes.title.lower() or needle in t.attributes.namespace.lower()
        ]
        if not matches:
            raise RuntimeError(f"No tool found matching {name!r}")
        if len(matches) > 1:
            names = ", ".join(t.attributes.title for t in matches)
            raise RuntimeError(f"Ambiguous tool name {name!r} — matches: {names}")
        return matches[0].id, matches[0].attributes.title

    def add_tool(self, name: ToolName | str) -> LightTool:
        """Install a tool on the device by name (e.g. 'calendar')."""
        from open_api_specification_client.api.default import post_api_device_tools
        from open_api_specification_client.models import (
            PostApiDeviceToolsBody,
            PostApiDeviceToolsBodyData,
            PostApiDeviceToolsBodyDataAttributes,
            PostApiDeviceToolsBodyDataType,
        )

        global_tool_id, title = self._resolve_global_tool_id(name)
        device_id = self._get_device_id()

        resp = self._l.call_api(
            post_api_device_tools.sync_detailed,
            client=self._l._api_client,
            body=PostApiDeviceToolsBody(
                data=PostApiDeviceToolsBodyData(
                    type_=PostApiDeviceToolsBodyDataType.DEVICE_TOOLS,
                    attributes=PostApiDeviceToolsBodyDataAttributes(
                        device_id=device_id,
                        tool_id=global_tool_id,
                    ),
                )
            ),
        )
        if resp.status_code not in (200, 201) or resp.parsed is None:
            raise RuntimeError(f"Install tool: {resp.status_code}")

        return LightTool(
            device_tool_id=resp.parsed.data.id,
            global_tool_id=global_tool_id,
            namespace="",
            component="",
            title=title,
        )

    def remove_tool(self, name: ToolName | str) -> None:
        """Uninstall a tool from the device by name (e.g. 'calendar')."""
        from open_api_specification_client.api.default import delete_api_device_tools_device_tool_id

        needle = name.lower()
        installed = self.get_tools()
        matches = [t for t in installed if needle in t.title.lower() or needle in t.namespace.lower()]
        if not matches:
            raise RuntimeError(f"No installed tool found matching {name!r}")
        if len(matches) > 1:
            names = ", ".join(t.title for t in matches)
            raise RuntimeError(f"Ambiguous tool name {name!r} — matches: {names}")

        resp = self._l.call_api(
            delete_api_device_tools_device_tool_id.sync_detailed,
            client=self._l._api_client,
            device_tool_id=matches[0].device_tool_id,
        )
        if not (200 <= resp.status_code < 300):
            raise RuntimeError(f"Remove tool: {resp.status_code}")
