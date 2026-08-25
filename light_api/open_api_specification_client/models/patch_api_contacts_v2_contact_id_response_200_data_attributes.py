from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PatchApiContactsV2ContactIdResponse200DataAttributes")


@_attrs_define
class PatchApiContactsV2ContactIdResponse200DataAttributes:
    """
    Attributes:
        first_name (str):
        last_name (str):
        number (str):
    """

    first_name: str
    last_name: str
    number: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        first_name = self.first_name

        last_name = self.last_name

        number = self.number

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "first_name": first_name,
                "last_name": last_name,
                "number": number,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        first_name = d.pop("first_name")

        last_name = d.pop("last_name")

        number = d.pop("number")

        patch_api_contacts_v2_contact_id_response_200_data_attributes = cls(
            first_name=first_name,
            last_name=last_name,
            number=number,
        )

        patch_api_contacts_v2_contact_id_response_200_data_attributes.additional_properties = d
        return patch_api_contacts_v2_contact_id_response_200_data_attributes

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
