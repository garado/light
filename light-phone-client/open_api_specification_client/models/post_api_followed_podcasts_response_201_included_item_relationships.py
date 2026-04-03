from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.post_api_followed_podcasts_response_201_included_item_relationships_device import (
        PostApiFollowedPodcastsResponse201IncludedItemRelationshipsDevice,
    )
    from ..models.post_api_followed_podcasts_response_201_included_item_relationships_tool import (
        PostApiFollowedPodcastsResponse201IncludedItemRelationshipsTool,
    )


T = TypeVar("T", bound="PostApiFollowedPodcastsResponse201IncludedItemRelationships")


@_attrs_define
class PostApiFollowedPodcastsResponse201IncludedItemRelationships:
    """
    Attributes:
        device (PostApiFollowedPodcastsResponse201IncludedItemRelationshipsDevice):
        tool (PostApiFollowedPodcastsResponse201IncludedItemRelationshipsTool):
    """

    device: PostApiFollowedPodcastsResponse201IncludedItemRelationshipsDevice
    tool: PostApiFollowedPodcastsResponse201IncludedItemRelationshipsTool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device = self.device.to_dict()

        tool = self.tool.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "device": device,
                "tool": tool,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_api_followed_podcasts_response_201_included_item_relationships_device import (
            PostApiFollowedPodcastsResponse201IncludedItemRelationshipsDevice,
        )
        from ..models.post_api_followed_podcasts_response_201_included_item_relationships_tool import (
            PostApiFollowedPodcastsResponse201IncludedItemRelationshipsTool,
        )

        d = dict(src_dict)
        device = PostApiFollowedPodcastsResponse201IncludedItemRelationshipsDevice.from_dict(d.pop("device"))

        tool = PostApiFollowedPodcastsResponse201IncludedItemRelationshipsTool.from_dict(d.pop("tool"))

        post_api_followed_podcasts_response_201_included_item_relationships = cls(
            device=device,
            tool=tool,
        )

        post_api_followed_podcasts_response_201_included_item_relationships.additional_properties = d
        return post_api_followed_podcasts_response_201_included_item_relationships

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
