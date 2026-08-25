from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.patch_api_devices_device_id_developer_mode_response_200_data_attributes import (
        PatchApiDevicesDeviceIdDeveloperModeResponse200DataAttributes,
    )


T = TypeVar("T", bound="PatchApiDevicesDeviceIdDeveloperModeResponse200Data")


@_attrs_define
class PatchApiDevicesDeviceIdDeveloperModeResponse200Data:
    """
    Attributes:
        id (str):
        type_ (str):
        attributes (PatchApiDevicesDeviceIdDeveloperModeResponse200DataAttributes):
    """

    id: str
    type_: str
    attributes: PatchApiDevicesDeviceIdDeveloperModeResponse200DataAttributes
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        type_ = self.type_

        attributes = self.attributes.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "type": type_,
                "attributes": attributes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.patch_api_devices_device_id_developer_mode_response_200_data_attributes import (
            PatchApiDevicesDeviceIdDeveloperModeResponse200DataAttributes,
        )

        d = dict(src_dict)
        id = d.pop("id")

        type_ = d.pop("type")

        attributes = PatchApiDevicesDeviceIdDeveloperModeResponse200DataAttributes.from_dict(d.pop("attributes"))

        patch_api_devices_device_id_developer_mode_response_200_data = cls(
            id=id,
            type_=type_,
            attributes=attributes,
        )

        patch_api_devices_device_id_developer_mode_response_200_data.additional_properties = d
        return patch_api_devices_device_id_developer_mode_response_200_data

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
