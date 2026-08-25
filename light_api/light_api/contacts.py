"""Contacts management for Light devices."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from open_api_specification_client.api.default import get_api_contacts_v2

if TYPE_CHECKING:
    from light_api.client import Light


@dataclass
class LightContact:
    id: str
    first_name: str
    last_name: str
    number: str


class LightContacts:
    def __init__(self, light: "Light") -> None:
        self._l = light

    def get_contacts(self) -> list[LightContact]:
        """Return every contact stored on this device."""
        device_id = self._l.current_device_id

        resp = self._l.call_api(
            get_api_contacts_v2.sync_detailed,
            client=self._l._api_client,
            device_id=device_id,
        )
        parsed = self._l._ensure_ok(
            resp, "Could not fetch contacts", require_parsed=True
        )

        return [
            LightContact(
                id=c.id,
                first_name=c.attributes.first_name,
                last_name=c.attributes.last_name,
                number=c.attributes.number,
            )
            for c in parsed.data
        ]
