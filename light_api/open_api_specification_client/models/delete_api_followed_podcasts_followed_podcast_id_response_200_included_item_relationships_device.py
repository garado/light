from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.delete_api_followed_podcasts_followed_podcast_id_response_200_included_item_relationships_device_data import (
        DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationshipsDeviceData,
    )


T = TypeVar("T", bound="DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationshipsDevice")


@_attrs_define
class DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationshipsDevice:
    """
    Attributes:
        data (DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationshipsDeviceData):
    """

    data: DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationshipsDeviceData
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
        from ..models.delete_api_followed_podcasts_followed_podcast_id_response_200_included_item_relationships_device_data import (
            DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationshipsDeviceData,
        )

        d = dict(src_dict)
        data = DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationshipsDeviceData.from_dict(
            d.pop("data")
        )

        delete_api_followed_podcasts_followed_podcast_id_response_200_included_item_relationships_device = cls(
            data=data,
        )

        delete_api_followed_podcasts_followed_podcast_id_response_200_included_item_relationships_device.additional_properties = d
        return delete_api_followed_podcasts_followed_podcast_id_response_200_included_item_relationships_device

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
