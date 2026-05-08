from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostApiDeviceToolsBodyDataAttributes")


@_attrs_define
class PostApiDeviceToolsBodyDataAttributes:
    """
    Attributes:
        device_id (str):
        tool_id (str):
        calendar (bool | Unset):
    """

    device_id: str
    tool_id: str
    calendar: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_id = self.device_id

        tool_id = self.tool_id

        calendar = self.calendar

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "device_id": device_id,
                "tool_id": tool_id,
            }
        )
        if calendar is not UNSET:
            field_dict["calendar"] = calendar

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        device_id = d.pop("device_id")

        tool_id = d.pop("tool_id")

        calendar = d.pop("calendar", UNSET)

        post_api_device_tools_body_data_attributes = cls(
            device_id=device_id,
            tool_id=tool_id,
            calendar=calendar,
        )

        post_api_device_tools_body_data_attributes.additional_properties = d
        return post_api_device_tools_body_data_attributes

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
