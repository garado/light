"""Manage installed Light Phone tools."""

import dataclasses
import logging
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING
        
from open_api_specification_client.api.default import (
    delete_api_device_tools_device_tool_id,
    get_api_devices,
    get_api_tools,
    post_api_device_tools,
)
from open_api_specification_client.models import (
    PostApiDeviceToolsBody,
    PostApiDeviceToolsBodyData,
    PostApiDeviceToolsBodyDataAttributes,
    PostApiDeviceToolsBodyDataType,
)

from light_api import cache

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
        if self._l._cache_enabled:
            cached = cache.load(cache.CacheModule.TOOLS, self._l._api_token)
            if cached is not None:
                return [LightTool(**t) for t in cached]

        devices_resp = self._l.call_api(
            get_api_devices.sync_detailed, client=self._l._api_client
        )
        devices = self._l._ensure_ok(
            devices_resp, "Could not fetch devices", require_data=True
        )

        device_id = self._l._select_device_id(devices)

        tools_resp = get_api_tools.sync_detailed(
            client=self._l._api_client, device_id=device_id
        )
        tools = self._l._ensure_ok(
            tools_resp, "Could not fetch tools", require_parsed=True
        )

        tool_info = {
            t.id: (t.attributes.namespace, t.attributes.component, t.attributes.title)
            for t in tools.data
        }

        results = []
        for item in self._l._device_tool_items(devices.included, device_id):
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

        results = sorted(results, key=lambda t: t.title.lower())

        if self._l._cache_enabled:
            cache.save(
                cache.CacheModule.TOOLS,
                self._l._api_token,
                [dataclasses.asdict(t) for t in results],
            )

        return results

    def _get_device_id(self) -> str:
        resp = self._l.call_api(
            get_api_devices.sync_detailed, client=self._l._api_client
        )
        devices = self._l._ensure_ok(resp, "Could not fetch devices", require_data=True)
        return self._l._select_device_id(devices)

    def _resolve_global_tool_id(self, name: str) -> tuple[str, str]:
        """Return (global_tool_id, title) for a tool matching name (case-insensitive)."""
        device_id = self._get_device_id()
        resp = get_api_tools.sync_detailed(
            client=self._l._api_client, device_id=device_id
        )
        tools = self._l._ensure_ok(resp, "Could not fetch tools", require_parsed=True)
        needle = name.lower()
        matches = [
            t
            for t in tools.data
            if needle in t.attributes.title.lower()
            or needle in t.attributes.namespace.lower()
        ]
        if not matches:
            raise RuntimeError(f"No tool found matching {name!r}")
        if len(matches) > 1:
            names = ", ".join(t.attributes.title for t in matches)
            raise RuntimeError(f"Ambiguous tool name {name!r} — matches: {names}")
        return matches[0].id, matches[0].attributes.title

    def add_tool(self, name: ToolName | str) -> LightTool:
        """Install a tool on the device by name (e.g. 'calendar')."""
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
        parsed = self._l._ensure_ok(
            resp, "Install tool", ok_codes=(200, 201), require_parsed=True
        )

        cache.invalidate(cache.CacheModule.TOOLS)

        return LightTool(
            device_tool_id=parsed.data.id,
            global_tool_id=global_tool_id,
            namespace="",
            component="",
            title=title,
        )

    def remove_tool(self, name: ToolName | str) -> None:
        """Uninstall a tool from the device by name (e.g. 'calendar')."""
        needle = name.lower()
        installed = self.get_tools()
        matches = [
            t
            for t in installed
            if needle in t.title.lower() or needle in t.namespace.lower()
        ]
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
        self._l._ensure_ok(resp, "Remove tool", ok_codes=range(200, 300))

        cache.invalidate(cache.CacheModule.TOOLS)
