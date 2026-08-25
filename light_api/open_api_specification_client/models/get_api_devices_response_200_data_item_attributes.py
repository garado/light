from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GetApiDevicesResponse200DataItemAttributes")


@_attrs_define
class GetApiDevicesResponse200DataItemAttributes:
    """
    Attributes:
        admin (bool):
        developer_mode (bool):
        device_type (str):
        imei (str):
        light_os_version_name (str):
        serial_number (str):
        sku (str):
    """

    admin: bool
    developer_mode: bool
    device_type: str
    imei: str
    light_os_version_name: str
    serial_number: str
    sku: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        admin = self.admin

        developer_mode = self.developer_mode

        device_type = self.device_type

        imei = self.imei

        light_os_version_name = self.light_os_version_name

        serial_number = self.serial_number

        sku = self.sku

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "admin": admin,
                "developer_mode": developer_mode,
                "device_type": device_type,
                "imei": imei,
                "light_os_version_name": light_os_version_name,
                "serial_number": serial_number,
                "sku": sku,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        admin = d.pop("admin")

        developer_mode = d.pop("developer_mode")

        device_type = d.pop("device_type")

        imei = d.pop("imei")

        light_os_version_name = d.pop("light_os_version_name")

        serial_number = d.pop("serial_number")

        sku = d.pop("sku")

        get_api_devices_response_200_data_item_attributes = cls(
            admin=admin,
            developer_mode=developer_mode,
            device_type=device_type,
            imei=imei,
            light_os_version_name=light_os_version_name,
            serial_number=serial_number,
            sku=sku,
        )

        get_api_devices_response_200_data_item_attributes.additional_properties = d
        return get_api_devices_response_200_data_item_attributes

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
