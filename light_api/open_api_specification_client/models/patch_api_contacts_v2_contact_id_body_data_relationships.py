from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.patch_api_contacts_v2_contact_id_body_data_relationships_device import (
        PatchApiContactsV2ContactIdBodyDataRelationshipsDevice,
    )


T = TypeVar("T", bound="PatchApiContactsV2ContactIdBodyDataRelationships")


@_attrs_define
class PatchApiContactsV2ContactIdBodyDataRelationships:
    """
    Attributes:
        device (PatchApiContactsV2ContactIdBodyDataRelationshipsDevice):
    """

    device: PatchApiContactsV2ContactIdBodyDataRelationshipsDevice
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device = self.device.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "device": device,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.patch_api_contacts_v2_contact_id_body_data_relationships_device import (
            PatchApiContactsV2ContactIdBodyDataRelationshipsDevice,
        )

        d = dict(src_dict)
        device = PatchApiContactsV2ContactIdBodyDataRelationshipsDevice.from_dict(d.pop("device"))

        patch_api_contacts_v2_contact_id_body_data_relationships = cls(
            device=device,
        )

        patch_api_contacts_v2_contact_id_body_data_relationships.additional_properties = d
        return patch_api_contacts_v2_contact_id_body_data_relationships

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
