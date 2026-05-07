from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_api_device_tools_response_201_data_relationships_device import (
        PostApiDeviceToolsResponse201DataRelationshipsDevice,
    )
    from ..models.post_api_device_tools_response_201_data_relationships_tool import (
        PostApiDeviceToolsResponse201DataRelationshipsTool,
    )


T = TypeVar("T", bound="PostApiDeviceToolsResponse201DataRelationships")


@_attrs_define
class PostApiDeviceToolsResponse201DataRelationships:
    """
    Attributes:
        device (PostApiDeviceToolsResponse201DataRelationshipsDevice | Unset):
        tool (PostApiDeviceToolsResponse201DataRelationshipsTool | Unset):
    """

    device: PostApiDeviceToolsResponse201DataRelationshipsDevice | Unset = UNSET
    tool: PostApiDeviceToolsResponse201DataRelationshipsTool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device: dict[str, Any] | Unset = UNSET
        if not isinstance(self.device, Unset):
            device = self.device.to_dict()

        tool: dict[str, Any] | Unset = UNSET
        if not isinstance(self.tool, Unset):
            tool = self.tool.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if device is not UNSET:
            field_dict["device"] = device
        if tool is not UNSET:
            field_dict["tool"] = tool

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_api_device_tools_response_201_data_relationships_device import (
            PostApiDeviceToolsResponse201DataRelationshipsDevice,
        )
        from ..models.post_api_device_tools_response_201_data_relationships_tool import (
            PostApiDeviceToolsResponse201DataRelationshipsTool,
        )

        d = dict(src_dict)
        _device = d.pop("device", UNSET)
        device: PostApiDeviceToolsResponse201DataRelationshipsDevice | Unset
        if isinstance(_device, Unset):
            device = UNSET
        else:
            device = PostApiDeviceToolsResponse201DataRelationshipsDevice.from_dict(_device)

        _tool = d.pop("tool", UNSET)
        tool: PostApiDeviceToolsResponse201DataRelationshipsTool | Unset
        if isinstance(_tool, Unset):
            tool = UNSET
        else:
            tool = PostApiDeviceToolsResponse201DataRelationshipsTool.from_dict(_tool)

        post_api_device_tools_response_201_data_relationships = cls(
            device=device,
            tool=tool,
        )

        post_api_device_tools_response_201_data_relationships.additional_properties = d
        return post_api_device_tools_response_201_data_relationships

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
