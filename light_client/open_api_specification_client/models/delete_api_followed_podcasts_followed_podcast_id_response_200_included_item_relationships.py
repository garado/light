from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.delete_api_followed_podcasts_followed_podcast_id_response_200_included_item_relationships_device import (
        DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationshipsDevice,
    )
    from ..models.delete_api_followed_podcasts_followed_podcast_id_response_200_included_item_relationships_tool import (
        DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationshipsTool,
    )


T = TypeVar("T", bound="DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationships")


@_attrs_define
class DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationships:
    """
    Attributes:
        device (DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationshipsDevice):
        tool (DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationshipsTool):
    """

    device: DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationshipsDevice
    tool: DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationshipsTool
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
        from ..models.delete_api_followed_podcasts_followed_podcast_id_response_200_included_item_relationships_device import (
            DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationshipsDevice,
        )
        from ..models.delete_api_followed_podcasts_followed_podcast_id_response_200_included_item_relationships_tool import (
            DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationshipsTool,
        )

        d = dict(src_dict)
        device = DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationshipsDevice.from_dict(
            d.pop("device")
        )

        tool = DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationshipsTool.from_dict(
            d.pop("tool")
        )

        delete_api_followed_podcasts_followed_podcast_id_response_200_included_item_relationships = cls(
            device=device,
            tool=tool,
        )

        delete_api_followed_podcasts_followed_podcast_id_response_200_included_item_relationships.additional_properties = d
        return delete_api_followed_podcasts_followed_podcast_id_response_200_included_item_relationships

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
