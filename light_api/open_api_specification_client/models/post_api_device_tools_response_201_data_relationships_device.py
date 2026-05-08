from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_api_device_tools_response_201_data_relationships_device_data import (
        PostApiDeviceToolsResponse201DataRelationshipsDeviceData,
    )


T = TypeVar("T", bound="PostApiDeviceToolsResponse201DataRelationshipsDevice")


@_attrs_define
class PostApiDeviceToolsResponse201DataRelationshipsDevice:
    """
    Attributes:
        data (PostApiDeviceToolsResponse201DataRelationshipsDeviceData | Unset):
    """

    data: PostApiDeviceToolsResponse201DataRelationshipsDeviceData | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.data, Unset):
            data = self.data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if data is not UNSET:
            field_dict["data"] = data

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_api_device_tools_response_201_data_relationships_device_data import (
            PostApiDeviceToolsResponse201DataRelationshipsDeviceData,
        )

        d = dict(src_dict)
        _data = d.pop("data", UNSET)
        data: PostApiDeviceToolsResponse201DataRelationshipsDeviceData | Unset
        if isinstance(_data, Unset):
            data = UNSET
        else:
            data = PostApiDeviceToolsResponse201DataRelationshipsDeviceData.from_dict(_data)

        post_api_device_tools_response_201_data_relationships_device = cls(
            data=data,
        )

        post_api_device_tools_response_201_data_relationships_device.additional_properties = d
        return post_api_device_tools_response_201_data_relationships_device

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
