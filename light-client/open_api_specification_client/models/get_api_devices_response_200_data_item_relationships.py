from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_api_devices_response_200_data_item_relationships_device_tool_location import (
        GetApiDevicesResponse200DataItemRelationshipsDeviceToolLocation,
    )
    from ..models.get_api_devices_response_200_data_item_relationships_device_tools import (
        GetApiDevicesResponse200DataItemRelationshipsDeviceTools,
    )
    from ..models.get_api_devices_response_200_data_item_relationships_sim import (
        GetApiDevicesResponse200DataItemRelationshipsSim,
    )
    from ..models.get_api_devices_response_200_data_item_relationships_user import (
        GetApiDevicesResponse200DataItemRelationshipsUser,
    )


T = TypeVar("T", bound="GetApiDevicesResponse200DataItemRelationships")


@_attrs_define
class GetApiDevicesResponse200DataItemRelationships:
    """
    Attributes:
        device_tool_location (GetApiDevicesResponse200DataItemRelationshipsDeviceToolLocation):
        device_tools (GetApiDevicesResponse200DataItemRelationshipsDeviceTools):
        sim (GetApiDevicesResponse200DataItemRelationshipsSim):
        user (GetApiDevicesResponse200DataItemRelationshipsUser):
    """

    device_tool_location: GetApiDevicesResponse200DataItemRelationshipsDeviceToolLocation
    device_tools: GetApiDevicesResponse200DataItemRelationshipsDeviceTools
    sim: GetApiDevicesResponse200DataItemRelationshipsSim
    user: GetApiDevicesResponse200DataItemRelationshipsUser
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_tool_location = self.device_tool_location.to_dict()

        device_tools = self.device_tools.to_dict()

        sim = self.sim.to_dict()

        user = self.user.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "device_tool_location": device_tool_location,
                "device_tools": device_tools,
                "sim": sim,
                "user": user,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_api_devices_response_200_data_item_relationships_device_tool_location import (
            GetApiDevicesResponse200DataItemRelationshipsDeviceToolLocation,
        )
        from ..models.get_api_devices_response_200_data_item_relationships_device_tools import (
            GetApiDevicesResponse200DataItemRelationshipsDeviceTools,
        )
        from ..models.get_api_devices_response_200_data_item_relationships_sim import (
            GetApiDevicesResponse200DataItemRelationshipsSim,
        )
        from ..models.get_api_devices_response_200_data_item_relationships_user import (
            GetApiDevicesResponse200DataItemRelationshipsUser,
        )

        d = dict(src_dict)
        device_tool_location = GetApiDevicesResponse200DataItemRelationshipsDeviceToolLocation.from_dict(
            d.pop("device_tool_location")
        )

        device_tools = GetApiDevicesResponse200DataItemRelationshipsDeviceTools.from_dict(d.pop("device_tools"))

        sim = GetApiDevicesResponse200DataItemRelationshipsSim.from_dict(d.pop("sim"))

        user = GetApiDevicesResponse200DataItemRelationshipsUser.from_dict(d.pop("user"))

        get_api_devices_response_200_data_item_relationships = cls(
            device_tool_location=device_tool_location,
            device_tools=device_tools,
            sim=sim,
            user=user,
        )

        get_api_devices_response_200_data_item_relationships.additional_properties = d
        return get_api_devices_response_200_data_item_relationships

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
