from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.post_api_followed_podcasts_body_data_relationships_podcast_data_type import (
    PostApiFollowedPodcastsBodyDataRelationshipsPodcastDataType,
)

T = TypeVar("T", bound="PostApiFollowedPodcastsBodyDataRelationshipsPodcastData")


@_attrs_define
class PostApiFollowedPodcastsBodyDataRelationshipsPodcastData:
    """
    Attributes:
        type_ (PostApiFollowedPodcastsBodyDataRelationshipsPodcastDataType):
        id (str):
    """

    type_: PostApiFollowedPodcastsBodyDataRelationshipsPodcastDataType
    id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        id = self.id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "id": id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = PostApiFollowedPodcastsBodyDataRelationshipsPodcastDataType(d.pop("type"))

        id = d.pop("id")

        post_api_followed_podcasts_body_data_relationships_podcast_data = cls(
            type_=type_,
            id=id,
        )

        post_api_followed_podcasts_body_data_relationships_podcast_data.additional_properties = d
        return post_api_followed_podcasts_body_data_relationships_podcast_data

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
