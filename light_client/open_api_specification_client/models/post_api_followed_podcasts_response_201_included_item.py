from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_api_followed_podcasts_response_201_included_item_attributes import (
        PostApiFollowedPodcastsResponse201IncludedItemAttributes,
    )
    from ..models.post_api_followed_podcasts_response_201_included_item_relationships import (
        PostApiFollowedPodcastsResponse201IncludedItemRelationships,
    )


T = TypeVar("T", bound="PostApiFollowedPodcastsResponse201IncludedItem")


@_attrs_define
class PostApiFollowedPodcastsResponse201IncludedItem:
    """
    Attributes:
        attributes (PostApiFollowedPodcastsResponse201IncludedItemAttributes):
        id (str):
        type_ (str):
        relationships (PostApiFollowedPodcastsResponse201IncludedItemRelationships | Unset):
    """

    attributes: PostApiFollowedPodcastsResponse201IncludedItemAttributes
    id: str
    type_: str
    relationships: PostApiFollowedPodcastsResponse201IncludedItemRelationships | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        attributes = self.attributes.to_dict()

        id = self.id

        type_ = self.type_

        relationships: dict[str, Any] | Unset = UNSET
        if not isinstance(self.relationships, Unset):
            relationships = self.relationships.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "attributes": attributes,
                "id": id,
                "type": type_,
            }
        )
        if relationships is not UNSET:
            field_dict["relationships"] = relationships

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_api_followed_podcasts_response_201_included_item_attributes import (
            PostApiFollowedPodcastsResponse201IncludedItemAttributes,
        )
        from ..models.post_api_followed_podcasts_response_201_included_item_relationships import (
            PostApiFollowedPodcastsResponse201IncludedItemRelationships,
        )

        d = dict(src_dict)
        attributes = PostApiFollowedPodcastsResponse201IncludedItemAttributes.from_dict(d.pop("attributes"))

        id = d.pop("id")

        type_ = d.pop("type")

        _relationships = d.pop("relationships", UNSET)
        relationships: PostApiFollowedPodcastsResponse201IncludedItemRelationships | Unset
        if isinstance(_relationships, Unset):
            relationships = UNSET
        else:
            relationships = PostApiFollowedPodcastsResponse201IncludedItemRelationships.from_dict(_relationships)

        post_api_followed_podcasts_response_201_included_item = cls(
            attributes=attributes,
            id=id,
            type_=type_,
            relationships=relationships,
        )

        post_api_followed_podcasts_response_201_included_item.additional_properties = d
        return post_api_followed_podcasts_response_201_included_item

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
