from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_api_devices_response_200_included_item_relationships_device import (
        GetApiDevicesResponse200IncludedItemRelationshipsDevice,
    )
    from ..models.get_api_devices_response_200_included_item_relationships_tool import (
        GetApiDevicesResponse200IncludedItemRelationshipsTool,
    )
    from ..models.get_api_devices_response_200_included_item_relationships_user import (
        GetApiDevicesResponse200IncludedItemRelationshipsUser,
    )


T = TypeVar("T", bound="GetApiDevicesResponse200IncludedItemRelationships")


@_attrs_define
class GetApiDevicesResponse200IncludedItemRelationships:
    """
    Attributes:
        device (GetApiDevicesResponse200IncludedItemRelationshipsDevice):
        tool (GetApiDevicesResponse200IncludedItemRelationshipsTool | Unset):
        user (GetApiDevicesResponse200IncludedItemRelationshipsUser | Unset):
    """

    device: GetApiDevicesResponse200IncludedItemRelationshipsDevice
    tool: GetApiDevicesResponse200IncludedItemRelationshipsTool | Unset = UNSET
    user: GetApiDevicesResponse200IncludedItemRelationshipsUser | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device = self.device.to_dict()

        tool: dict[str, Any] | Unset = UNSET
        if not isinstance(self.tool, Unset):
            tool = self.tool.to_dict()

        user: dict[str, Any] | Unset = UNSET
        if not isinstance(self.user, Unset):
            user = self.user.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "device": device,
            }
        )
        if tool is not UNSET:
            field_dict["tool"] = tool
        if user is not UNSET:
            field_dict["user"] = user

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_api_devices_response_200_included_item_relationships_device import (
            GetApiDevicesResponse200IncludedItemRelationshipsDevice,
        )
        from ..models.get_api_devices_response_200_included_item_relationships_tool import (
            GetApiDevicesResponse200IncludedItemRelationshipsTool,
        )
        from ..models.get_api_devices_response_200_included_item_relationships_user import (
            GetApiDevicesResponse200IncludedItemRelationshipsUser,
        )

        d = dict(src_dict)
        device = GetApiDevicesResponse200IncludedItemRelationshipsDevice.from_dict(d.pop("device"))

        _tool = d.pop("tool", UNSET)
        tool: GetApiDevicesResponse200IncludedItemRelationshipsTool | Unset
        if isinstance(_tool, Unset):
            tool = UNSET
        else:
            tool = GetApiDevicesResponse200IncludedItemRelationshipsTool.from_dict(_tool)

        _user = d.pop("user", UNSET)
        user: GetApiDevicesResponse200IncludedItemRelationshipsUser | Unset
        if isinstance(_user, Unset):
            user = UNSET
        else:
            user = GetApiDevicesResponse200IncludedItemRelationshipsUser.from_dict(_user)

        get_api_devices_response_200_included_item_relationships = cls(
            device=device,
            tool=tool,
            user=user,
        )

        get_api_devices_response_200_included_item_relationships.additional_properties = d
        return get_api_devices_response_200_included_item_relationships

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
