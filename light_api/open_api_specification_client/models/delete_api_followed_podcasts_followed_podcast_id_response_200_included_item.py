from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.delete_api_followed_podcasts_followed_podcast_id_response_200_included_item_attributes import (
        DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemAttributes,
    )
    from ..models.delete_api_followed_podcasts_followed_podcast_id_response_200_included_item_relationships import (
        DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationships,
    )


T = TypeVar("T", bound="DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItem")


@_attrs_define
class DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItem:
    """
    Attributes:
        attributes (DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemAttributes):
        id (str):
        type_ (str):
        relationships (DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationships | Unset):
    """

    attributes: DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemAttributes
    id: str
    type_: str
    relationships: DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationships | Unset = UNSET
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
        from ..models.delete_api_followed_podcasts_followed_podcast_id_response_200_included_item_attributes import (
            DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemAttributes,
        )
        from ..models.delete_api_followed_podcasts_followed_podcast_id_response_200_included_item_relationships import (
            DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationships,
        )

        d = dict(src_dict)
        attributes = DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemAttributes.from_dict(
            d.pop("attributes")
        )

        id = d.pop("id")

        type_ = d.pop("type")

        _relationships = d.pop("relationships", UNSET)
        relationships: DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationships | Unset
        if isinstance(_relationships, Unset):
            relationships = UNSET
        else:
            relationships = DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemRelationships.from_dict(
                _relationships
            )

        delete_api_followed_podcasts_followed_podcast_id_response_200_included_item = cls(
            attributes=attributes,
            id=id,
            type_=type_,
            relationships=relationships,
        )

        delete_api_followed_podcasts_followed_podcast_id_response_200_included_item.additional_properties = d
        return delete_api_followed_podcasts_followed_podcast_id_response_200_included_item

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
