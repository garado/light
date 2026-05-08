from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationshipsDeviceData")


@_attrs_define
class DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationshipsDeviceData:
    """
    Attributes:
        id (str):
        type_ (str):
    """

    id: str
    type_: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "type": type_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        type_ = d.pop("type")

        delete_api_followed_podcasts_followed_podcast_id_response_200_included_item_relationships_device_data = cls(
            id=id,
            type_=type_,
        )

        delete_api_followed_podcasts_followed_podcast_id_response_200_included_item_relationships_device_data.additional_properties = d
        return delete_api_followed_podcasts_followed_podcast_id_response_200_included_item_relationships_device_data

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
