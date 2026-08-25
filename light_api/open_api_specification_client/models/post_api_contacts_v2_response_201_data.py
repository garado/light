from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.post_api_contacts_v2_response_201_data_attributes import PostApiContactsV2Response201DataAttributes
    from ..models.post_api_contacts_v2_response_201_data_relationships import (
        PostApiContactsV2Response201DataRelationships,
    )


T = TypeVar("T", bound="PostApiContactsV2Response201Data")


@_attrs_define
class PostApiContactsV2Response201Data:
    """
    Attributes:
        attributes (PostApiContactsV2Response201DataAttributes):
        id (str):
        relationships (PostApiContactsV2Response201DataRelationships):
        type_ (str):
    """

    attributes: PostApiContactsV2Response201DataAttributes
    id: str
    relationships: PostApiContactsV2Response201DataRelationships
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
        from ..models.post_api_contacts_v2_response_201_data_attributes import (
            PostApiContactsV2Response201DataAttributes,
        )
        from ..models.post_api_contacts_v2_response_201_data_relationships import (
            PostApiContactsV2Response201DataRelationships,
        )

        d = dict(src_dict)
        attributes = PostApiContactsV2Response201DataAttributes.from_dict(d.pop("attributes"))

        id = d.pop("id")

        relationships = PostApiContactsV2Response201DataRelationships.from_dict(d.pop("relationships"))

        type_ = d.pop("type")

        post_api_contacts_v2_response_201_data = cls(
            attributes=attributes,
            id=id,
            relationships=relationships,
            type_=type_,
        )

        post_api_contacts_v2_response_201_data.additional_properties = d
        return post_api_contacts_v2_response_201_data

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
