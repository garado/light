from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_api_devices_response_200_data_item_relationships_device_tools_data_item import (
        GetApiDevicesResponse200DataItemRelationshipsDeviceToolsDataItem,
    )


T = TypeVar("T", bound="GetApiDevicesResponse200DataItemRelationshipsDeviceTools")


@_attrs_define
class GetApiDevicesResponse200DataItemRelationshipsDeviceTools:
    """
    Attributes:
        data (list[GetApiDevicesResponse200DataItemRelationshipsDeviceToolsDataItem]):
    """

    data: list[GetApiDevicesResponse200DataItemRelationshipsDeviceToolsDataItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_api_devices_response_200_data_item_relationships_device_tools_data_item import (
            GetApiDevicesResponse200DataItemRelationshipsDeviceToolsDataItem,
        )

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = GetApiDevicesResponse200DataItemRelationshipsDeviceToolsDataItem.from_dict(data_item_data)

            data.append(data_item)

        get_api_devices_response_200_data_item_relationships_device_tools = cls(
            data=data,
        )

        get_api_devices_response_200_data_item_relationships_device_tools.additional_properties = d
        return get_api_devices_response_200_data_item_relationships_device_tools

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
