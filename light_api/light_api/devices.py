"""Device introspection."""

import dataclasses
from dataclasses import dataclass
from typing import TYPE_CHECKING

from open_api_specification_client.api.default import (
    get_api_devices,
    patch_api_devices_device_id_developer_mode,
)
from open_api_specification_client.models import (
    PatchApiDevicesDeviceIdDeveloperModeBody,
    PatchApiDevicesDeviceIdDeveloperModeBodyData,
    PatchApiDevicesDeviceIdDeveloperModeBodyDataAttributes,
    PatchApiDevicesDeviceIdDeveloperModeBodyDataType,
)
from open_api_specification_client.types import Unset

from light_api import cache

if TYPE_CHECKING:
    from light_api.client import Light


@dataclass
class LightDevice:
    id: str
    phone_number: str | None
    serial_number: str
    sku: str
    developer_mode: bool | None


class LightDevices:
    def __init__(self, light: "Light") -> None:
        self._l = light

    def list_devices(self) -> list[LightDevice]:
        """Return every device registered on this account."""
        if self._l._cache_enabled:
            cached = cache.load(cache.CacheModule.DEVICES, self._l._api_token)
            if cached is not None:
                return [LightDevice(**d) for d in cached]

        resp = self._l.call_api(
            get_api_devices.sync_detailed, client=self._l._api_client
        )
        devices = self._l._ensure_ok(resp, "Could not fetch devices", require_data=True)

        phone_by_device = dict(self._l._device_phone_numbers(devices.included))

        result = [
            LightDevice(
                id=d.id,
                phone_number=phone_by_device.get(d.id),
                serial_number=d.attributes.serial_number,
                sku=d.attributes.sku,
                developer_mode=(
                    None
                    if isinstance(d.attributes.developer_mode, Unset)
                    else d.attributes.developer_mode
                ),
            )
            for d in devices.data
        ]

        if self._l._cache_enabled:
            cache.save(
                cache.CacheModule.DEVICES,
                self._l._api_token,
                [dataclasses.asdict(d) for d in result],
            )

        return result

    def set_developer_mode(self, device_id: str, enabled: bool) -> bool:
        """Enable or disable developer mode on a device. Returns the new state."""
        resp = self._l.call_api(
            patch_api_devices_device_id_developer_mode.sync_detailed,
            device_id=device_id,
            client=self._l._api_client,
            body=PatchApiDevicesDeviceIdDeveloperModeBody(
                data=PatchApiDevicesDeviceIdDeveloperModeBodyData(
                    id=device_id,
                    type_=PatchApiDevicesDeviceIdDeveloperModeBodyDataType.DEVICE,
                    attributes=PatchApiDevicesDeviceIdDeveloperModeBodyDataAttributes(
                        developer_mode=enabled
                    ),
                )
            ),
        )
        parsed = self._l._ensure_ok(
            resp, "Could not set developer mode", require_parsed=True
        )

        cache.invalidate(cache.CacheModule.DEVICES)

        return parsed.data.attributes.developer_mode
