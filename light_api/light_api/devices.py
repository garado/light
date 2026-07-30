"""Device introspection."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from light_api.client import Light


@dataclass
class LightDevice:
    id: str
    phone_number: str | None
    serial_number: str
    sku: str


class LightDevices:
    def __init__(self, light: "Light") -> None:
        self._l = light

    def list_devices(self) -> list[LightDevice]:
        """Return every device registered on this account."""
        from open_api_specification_client.api.default import get_api_devices

        resp = self._l.call_api(
            get_api_devices.sync_detailed, client=self._l._api_client
        )
        devices = self._l._ensure_ok(resp, "Could not fetch devices", require_data=True)

        phone_by_device = dict(self._l._device_phone_numbers(devices.included))

        return [
            LightDevice(
                id=d.id,
                phone_number=phone_by_device.get(d.id),
                serial_number=d.attributes.serial_number,
                sku=d.attributes.sku,
            )
            for d in devices.data
        ]
