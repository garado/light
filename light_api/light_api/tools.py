"""Installed tools introspection for Light devices."""

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from light_api.client import Light

log = logging.getLogger(f"light.{__name__}")


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

        device_id = devices_resp.parsed.data[0].id

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
            if isinstance(item.relationships.tool, Unset):
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
