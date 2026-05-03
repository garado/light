from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.post_api_followed_podcasts_response_201_included_item_relationships_device_data import (
        PostApiFollowedPodcastsResponse201IncludedItemRelationshipsDeviceData,
    )


T = TypeVar("T", bound="PostApiFollowedPodcastsResponse201IncludedItemRelationshipsDevice")


@_attrs_define
class PostApiFollowedPodcastsResponse201IncludedItemRelationshipsDevice:
    """
    Attributes:
        data (PostApiFollowedPodcastsResponse201IncludedItemRelationshipsDeviceData):
    """

    data: PostApiFollowedPodcastsResponse201IncludedItemRelationshipsDeviceData
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = self.data.to_dict()

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
        from ..models.post_api_followed_podcasts_response_201_included_item_relationships_device_data import (
            PostApiFollowedPodcastsResponse201IncludedItemRelationshipsDeviceData,
        )

        d = dict(src_dict)
        data = PostApiFollowedPodcastsResponse201IncludedItemRelationshipsDeviceData.from_dict(d.pop("data"))

        post_api_followed_podcasts_response_201_included_item_relationships_device = cls(
            data=data,
        )

        post_api_followed_podcasts_response_201_included_item_relationships_device.additional_properties = d
        return post_api_followed_podcasts_response_201_included_item_relationships_device

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
