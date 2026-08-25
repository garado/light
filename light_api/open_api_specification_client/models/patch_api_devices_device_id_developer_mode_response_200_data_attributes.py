from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PatchApiDevicesDeviceIdDeveloperModeResponse200DataAttributes")


@_attrs_define
class PatchApiDevicesDeviceIdDeveloperModeResponse200DataAttributes:
    """
    Attributes:
        developer_mode (bool):
    """

    developer_mode: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        developer_mode = self.developer_mode

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "developer_mode": developer_mode,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        developer_mode = d.pop("developer_mode")

        patch_api_devices_device_id_developer_mode_response_200_data_attributes = cls(
            developer_mode=developer_mode,
        )

        patch_api_devices_device_id_developer_mode_response_200_data_attributes.additional_properties = d
        return patch_api_devices_device_id_developer_mode_response_200_data_attributes

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
