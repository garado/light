from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.delete_api_followed_podcasts_followed_podcast_id_response_200_data_item_relationships_device_tool import (
        DeleteApiFollowedPodcastsFollowedPodcastIdResponse200DataItemRelationshipsDeviceTool,
    )
    from ..models.delete_api_followed_podcasts_followed_podcast_id_response_200_data_item_relationships_podcast import (
        DeleteApiFollowedPodcastsFollowedPodcastIdResponse200DataItemRelationshipsPodcast,
    )


T = TypeVar("T", bound="DeleteApiFollowedPodcastsFollowedPodcastIdResponse200DataItemRelationships")


@_attrs_define
class DeleteApiFollowedPodcastsFollowedPodcastIdResponse200DataItemRelationships:
    """
    Attributes:
        device_tool (DeleteApiFollowedPodcastsFollowedPodcastIdResponse200DataItemRelationshipsDeviceTool):
        podcast (DeleteApiFollowedPodcastsFollowedPodcastIdResponse200DataItemRelationshipsPodcast):
    """

    device_tool: DeleteApiFollowedPodcastsFollowedPodcastIdResponse200DataItemRelationshipsDeviceTool
    podcast: DeleteApiFollowedPodcastsFollowedPodcastIdResponse200DataItemRelationshipsPodcast
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_tool = self.device_tool.to_dict()

        podcast = self.podcast.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "device_tool": device_tool,
                "podcast": podcast,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.delete_api_followed_podcasts_followed_podcast_id_response_200_data_item_relationships_device_tool import (
            DeleteApiFollowedPodcastsFollowedPodcastIdResponse200DataItemRelationshipsDeviceTool,
        )
        from ..models.delete_api_followed_podcasts_followed_podcast_id_response_200_data_item_relationships_podcast import (
            DeleteApiFollowedPodcastsFollowedPodcastIdResponse200DataItemRelationshipsPodcast,
        )

        d = dict(src_dict)
        device_tool = DeleteApiFollowedPodcastsFollowedPodcastIdResponse200DataItemRelationshipsDeviceTool.from_dict(
            d.pop("device_tool")
        )

        podcast = DeleteApiFollowedPodcastsFollowedPodcastIdResponse200DataItemRelationshipsPodcast.from_dict(
            d.pop("podcast")
        )

        delete_api_followed_podcasts_followed_podcast_id_response_200_data_item_relationships = cls(
            device_tool=device_tool,
            podcast=podcast,
        )

        delete_api_followed_podcasts_followed_podcast_id_response_200_data_item_relationships.additional_properties = d
        return delete_api_followed_podcasts_followed_podcast_id_response_200_data_item_relationships

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
