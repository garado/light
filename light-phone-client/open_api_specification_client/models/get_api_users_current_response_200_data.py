from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_api_users_current_response_200_data_attributes import GetApiUsersCurrentResponse200DataAttributes
    from ..models.get_api_users_current_response_200_data_relationships import (
        GetApiUsersCurrentResponse200DataRelationships,
    )


T = TypeVar("T", bound="GetApiUsersCurrentResponse200Data")


@_attrs_define
class GetApiUsersCurrentResponse200Data:
    """
    Attributes:
        attributes (GetApiUsersCurrentResponse200DataAttributes):
        id (str):
        relationships (GetApiUsersCurrentResponse200DataRelationships):
        type_ (str):
    """

    attributes: GetApiUsersCurrentResponse200DataAttributes
    id: str
    relationships: GetApiUsersCurrentResponse200DataRelationships
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
        from ..models.get_api_users_current_response_200_data_attributes import (
            GetApiUsersCurrentResponse200DataAttributes,
        )
        from ..models.get_api_users_current_response_200_data_relationships import (
            GetApiUsersCurrentResponse200DataRelationships,
        )

        d = dict(src_dict)
        attributes = GetApiUsersCurrentResponse200DataAttributes.from_dict(d.pop("attributes"))

        id = d.pop("id")

        relationships = GetApiUsersCurrentResponse200DataRelationships.from_dict(d.pop("relationships"))

        type_ = d.pop("type")

        get_api_users_current_response_200_data = cls(
            attributes=attributes,
            id=id,
            relationships=relationships,
            type_=type_,
        )

        get_api_users_current_response_200_data.additional_properties = d
        return get_api_users_current_response_200_data

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
