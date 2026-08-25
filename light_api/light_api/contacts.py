"""Contacts management for Light devices."""

import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

from open_api_specification_client.api.default import (
    get_api_contacts_v2,
    patch_api_contacts_v2_contact_id,
    post_api_contacts_v2,
)
from open_api_specification_client.models import (
    PatchApiContactsV2ContactIdBody,
    PatchApiContactsV2ContactIdBodyData,
    PatchApiContactsV2ContactIdBodyDataAttributes,
    PatchApiContactsV2ContactIdBodyDataRelationships,
    PatchApiContactsV2ContactIdBodyDataRelationshipsDevice,
    PatchApiContactsV2ContactIdBodyDataRelationshipsDeviceData,
    PatchApiContactsV2ContactIdBodyDataRelationshipsDeviceDataType,
    PatchApiContactsV2ContactIdBodyDataType,
    PostApiContactsV2Body,
    PostApiContactsV2BodyData,
    PostApiContactsV2BodyDataAttributes,
    PostApiContactsV2BodyDataRelationships,
    PostApiContactsV2BodyDataRelationshipsDevice,
    PostApiContactsV2BodyDataRelationshipsDeviceData,
    PostApiContactsV2BodyDataRelationshipsDeviceDataType,
    PostApiContactsV2BodyDataType,
)

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

    def add_contact(
        self, first_name: str, last_name: str | None, number: str
    ) -> LightContact:
        """Add a contact to this device."""
        device_id = self._l.current_device_id
        contact_id = str(uuid.uuid4())  # IDs are generated clientside

        resp = self._l.call_api(
            post_api_contacts_v2.sync_detailed,
            client=self._l._api_client,
            body=PostApiContactsV2Body(
                data=PostApiContactsV2BodyData(
                    type_=PostApiContactsV2BodyDataType.CONTACTS,
                    id=contact_id,
                    attributes=PostApiContactsV2BodyDataAttributes(
                        first_name=first_name,
                        last_name=last_name or "",
                        number=number,
                    ),
                    relationships=PostApiContactsV2BodyDataRelationships(
                        device=PostApiContactsV2BodyDataRelationshipsDevice(
                            data=PostApiContactsV2BodyDataRelationshipsDeviceData(
                                id=device_id,
                                type_=PostApiContactsV2BodyDataRelationshipsDeviceDataType.DEVICES,
                            )
                        )
                    ),
                )
            ),
        )

        parsed = self._l._ensure_ok(
            resp, "Could not add contact", ok_codes=(200, 201), require_parsed=True
        )

        return LightContact(
            id=parsed.data.id,
            first_name=parsed.data.attributes.first_name,
            last_name=parsed.data.attributes.last_name,
            number=parsed.data.attributes.number,
        )

    def update_contact(
        self, contact_id: str, first_name: str, last_name: str | None, number: str
    ) -> LightContact:
        """Update a contact on this device.

        Replaces the full record. Callers must pass the full desired first/last/number,
        not just the field(s) being changed.
        """
        device_id = self._l.current_device_id

        resp = self._l.call_api(
            patch_api_contacts_v2_contact_id.sync_detailed,
            contact_id=contact_id,
            client=self._l._api_client,
            body=PatchApiContactsV2ContactIdBody(
                data=PatchApiContactsV2ContactIdBodyData(
                    type_=PatchApiContactsV2ContactIdBodyDataType.CONTACTS,
                    id=contact_id,
                    attributes=PatchApiContactsV2ContactIdBodyDataAttributes(
                        first_name=first_name,
                        last_name=last_name or "",
                        number=number,
                    ),
                    relationships=PatchApiContactsV2ContactIdBodyDataRelationships(
                        device=PatchApiContactsV2ContactIdBodyDataRelationshipsDevice(
                            data=PatchApiContactsV2ContactIdBodyDataRelationshipsDeviceData(
                                id=device_id,
                                type_=PatchApiContactsV2ContactIdBodyDataRelationshipsDeviceDataType.DEVICES,
                            )
                        )
                    ),
                )
            ),
        )

        parsed = self._l._ensure_ok(
            resp, "Could not update contact", require_parsed=True
        )

        return LightContact(
            id=parsed.data.id,
            first_name=parsed.data.attributes.first_name,
            last_name=parsed.data.attributes.last_name,
            number=parsed.data.attributes.number,
        )
