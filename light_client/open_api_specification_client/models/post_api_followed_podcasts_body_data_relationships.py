from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.post_api_followed_podcasts_body_data_relationships_device_tool import (
        PostApiFollowedPodcastsBodyDataRelationshipsDeviceTool,
    )
    from ..models.post_api_followed_podcasts_body_data_relationships_podcast import (
        PostApiFollowedPodcastsBodyDataRelationshipsPodcast,
    )


T = TypeVar("T", bound="PostApiFollowedPodcastsBodyDataRelationships")


@_attrs_define
class PostApiFollowedPodcastsBodyDataRelationships:
    """
    Attributes:
        device_tool (PostApiFollowedPodcastsBodyDataRelationshipsDeviceTool):
        podcast (PostApiFollowedPodcastsBodyDataRelationshipsPodcast):
    """

    device_tool: PostApiFollowedPodcastsBodyDataRelationshipsDeviceTool
    podcast: PostApiFollowedPodcastsBodyDataRelationshipsPodcast
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
        from ..models.post_api_followed_podcasts_body_data_relationships_device_tool import (
            PostApiFollowedPodcastsBodyDataRelationshipsDeviceTool,
        )
        from ..models.post_api_followed_podcasts_body_data_relationships_podcast import (
            PostApiFollowedPodcastsBodyDataRelationshipsPodcast,
        )

        d = dict(src_dict)
        device_tool = PostApiFollowedPodcastsBodyDataRelationshipsDeviceTool.from_dict(d.pop("device_tool"))

        podcast = PostApiFollowedPodcastsBodyDataRelationshipsPodcast.from_dict(d.pop("podcast"))

        post_api_followed_podcasts_body_data_relationships = cls(
            device_tool=device_tool,
            podcast=podcast,
        )

        post_api_followed_podcasts_body_data_relationships.additional_properties = d
        return post_api_followed_podcasts_body_data_relationships

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
