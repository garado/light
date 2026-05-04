from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.delete_api_followed_podcasts_followed_podcast_id_response_200_data_item_attributes import (
        DeleteApiFollowedPodcastsFollowedPodcastIdResponse200DataItemAttributes,
    )
    from ..models.delete_api_followed_podcasts_followed_podcast_id_response_200_data_item_relationships import (
        DeleteApiFollowedPodcastsFollowedPodcastIdResponse200DataItemRelationships,
    )


T = TypeVar("T", bound="DeleteApiFollowedPodcastsFollowedPodcastIdResponse200DataItem")


@_attrs_define
class DeleteApiFollowedPodcastsFollowedPodcastIdResponse200DataItem:
    """
    Attributes:
        attributes (DeleteApiFollowedPodcastsFollowedPodcastIdResponse200DataItemAttributes):
        id (str):
        relationships (DeleteApiFollowedPodcastsFollowedPodcastIdResponse200DataItemRelationships):
        type_ (str):
    """

    attributes: DeleteApiFollowedPodcastsFollowedPodcastIdResponse200DataItemAttributes
    id: str
    relationships: DeleteApiFollowedPodcastsFollowedPodcastIdResponse200DataItemRelationships
    type_: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        attributes = self.attributes.to_dict()

        id = self.id

        relationships = self.relationships.to_dict()

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "attributes": attributes,
                "id": id,
                "relationships": relationships,
                "type": type_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.delete_api_followed_podcasts_followed_podcast_id_response_200_data_item_attributes import (
            DeleteApiFollowedPodcastsFollowedPodcastIdResponse200DataItemAttributes,
        )
        from ..models.delete_api_followed_podcasts_followed_podcast_id_response_200_data_item_relationships import (
            DeleteApiFollowedPodcastsFollowedPodcastIdResponse200DataItemRelationships,
        )

        d = dict(src_dict)
        attributes = DeleteApiFollowedPodcastsFollowedPodcastIdResponse200DataItemAttributes.from_dict(
            d.pop("attributes")
        )

        id = d.pop("id")

        relationships = DeleteApiFollowedPodcastsFollowedPodcastIdResponse200DataItemRelationships.from_dict(
            d.pop("relationships")
        )

        type_ = d.pop("type")

        delete_api_followed_podcasts_followed_podcast_id_response_200_data_item = cls(
            attributes=attributes,
            id=id,
            relationships=relationships,
            type_=type_,
        )

        delete_api_followed_podcasts_followed_podcast_id_response_200_data_item.additional_properties = d
        return delete_api_followed_podcasts_followed_podcast_id_response_200_data_item

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
