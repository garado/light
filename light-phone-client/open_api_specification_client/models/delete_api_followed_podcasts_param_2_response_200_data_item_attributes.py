from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DeleteApiFollowedPodcastsParam2Response200DataItemAttributes")


@_attrs_define
class DeleteApiFollowedPodcastsParam2Response200DataItemAttributes:
    """
    Attributes:
        device_tool_id (str):
        podcast_id (str):
    """

    device_tool_id: str
    podcast_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_tool_id = self.device_tool_id

        podcast_id = self.podcast_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "device_tool_id": device_tool_id,
                "podcast_id": podcast_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        device_tool_id = d.pop("device_tool_id")

        podcast_id = d.pop("podcast_id")

        delete_api_followed_podcasts_param_2_response_200_data_item_attributes = cls(
            device_tool_id=device_tool_id,
            podcast_id=podcast_id,
        )

        delete_api_followed_podcasts_param_2_response_200_data_item_attributes.additional_properties = d
        return delete_api_followed_podcasts_param_2_response_200_data_item_attributes

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
