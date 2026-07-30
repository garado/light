"""Device introspection."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from open_api_specification_client.types import Unset

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
        if resp.status_code != 200 or not resp.parsed or not resp.parsed.data:
            raise RuntimeError(f"Could not fetch devices: {resp.status_code}")

        phone_by_device: dict[str, str] = {}
        for item in resp.parsed.included:
            if item.type_ != "sims" or isinstance(item.attributes.phone_number, Unset):
                continue
            phone_by_device[item.relationships.device.data.id] = (
                item.attributes.phone_number
            )

        return [
            LightDevice(
                id=d.id,
                phone_number=phone_by_device.get(d.id),
                serial_number=d.attributes.serial_number,
                sku=d.attributes.sku,
            )
            for d in resp.parsed.data
        ]
