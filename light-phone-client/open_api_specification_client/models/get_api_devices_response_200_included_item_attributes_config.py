from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_api_devices_response_200_included_item_attributes_config_address import (
        GetApiDevicesResponse200IncludedItemAttributesConfigAddress,
    )


T = TypeVar("T", bound="GetApiDevicesResponse200IncludedItemAttributesConfig")


@_attrs_define
class GetApiDevicesResponse200IncludedItemAttributesConfig:
    """
    Attributes:
        awaiting_migration (bool | Unset):
        device_tool_location_created (bool | Unset):
        address (GetApiDevicesResponse200IncludedItemAttributesConfigAddress | Unset):
        latitude (float | Unset):
        longitude (float | Unset):
    """

    awaiting_migration: bool | Unset = UNSET
    device_tool_location_created: bool | Unset = UNSET
    address: GetApiDevicesResponse200IncludedItemAttributesConfigAddress | Unset = UNSET
    latitude: float | Unset = UNSET
    longitude: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        awaiting_migration = self.awaiting_migration

        device_tool_location_created = self.device_tool_location_created

        address: dict[str, Any] | Unset = UNSET
        if not isinstance(self.address, Unset):
            address = self.address.to_dict()

        latitude = self.latitude

        longitude = self.longitude

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if awaiting_migration is not UNSET:
            field_dict["awaiting_migration"] = awaiting_migration
        if device_tool_location_created is not UNSET:
            field_dict["device_tool_location_created"] = device_tool_location_created
        if address is not UNSET:
            field_dict["address"] = address
        if latitude is not UNSET:
            field_dict["latitude"] = latitude
        if longitude is not UNSET:
            field_dict["longitude"] = longitude

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_api_devices_response_200_included_item_attributes_config_address import (
            GetApiDevicesResponse200IncludedItemAttributesConfigAddress,
        )

        d = dict(src_dict)
        awaiting_migration = d.pop("awaiting_migration", UNSET)

        device_tool_location_created = d.pop("device_tool_location_created", UNSET)

        _address = d.pop("address", UNSET)
        address: GetApiDevicesResponse200IncludedItemAttributesConfigAddress | Unset
        if isinstance(_address, Unset):
            address = UNSET
        else:
            address = GetApiDevicesResponse200IncludedItemAttributesConfigAddress.from_dict(_address)

        latitude = d.pop("latitude", UNSET)

        longitude = d.pop("longitude", UNSET)

        get_api_devices_response_200_included_item_attributes_config = cls(
            awaiting_migration=awaiting_migration,
            device_tool_location_created=device_tool_location_created,
            address=address,
            latitude=latitude,
            longitude=longitude,
        )

        get_api_devices_response_200_included_item_attributes_config.additional_properties = d
        return get_api_devices_response_200_included_item_attributes_config

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
