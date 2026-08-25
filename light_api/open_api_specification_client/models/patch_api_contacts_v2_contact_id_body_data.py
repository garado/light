from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.patch_api_contacts_v2_contact_id_body_data_type import PatchApiContactsV2ContactIdBodyDataType

if TYPE_CHECKING:
    from ..models.patch_api_contacts_v2_contact_id_body_data_attributes import (
        PatchApiContactsV2ContactIdBodyDataAttributes,
    )
    from ..models.patch_api_contacts_v2_contact_id_body_data_relationships import (
        PatchApiContactsV2ContactIdBodyDataRelationships,
    )


T = TypeVar("T", bound="PatchApiContactsV2ContactIdBodyData")


@_attrs_define
class PatchApiContactsV2ContactIdBodyData:
    """
    Attributes:
        type_ (PatchApiContactsV2ContactIdBodyDataType):
        id (str):
        attributes (PatchApiContactsV2ContactIdBodyDataAttributes):
        relationships (PatchApiContactsV2ContactIdBodyDataRelationships):
    """

    type_: PatchApiContactsV2ContactIdBodyDataType
    id: str
    attributes: PatchApiContactsV2ContactIdBodyDataAttributes
    relationships: PatchApiContactsV2ContactIdBodyDataRelationships
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        id = self.id

        attributes = self.attributes.to_dict()

        relationships = self.relationships.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "id": id,
                "attributes": attributes,
                "relationships": relationships,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.patch_api_contacts_v2_contact_id_body_data_attributes import (
            PatchApiContactsV2ContactIdBodyDataAttributes,
        )
        from ..models.patch_api_contacts_v2_contact_id_body_data_relationships import (
            PatchApiContactsV2ContactIdBodyDataRelationships,
        )

        d = dict(src_dict)
        type_ = PatchApiContactsV2ContactIdBodyDataType(d.pop("type"))

        id = d.pop("id")

        attributes = PatchApiContactsV2ContactIdBodyDataAttributes.from_dict(d.pop("attributes"))

        relationships = PatchApiContactsV2ContactIdBodyDataRelationships.from_dict(d.pop("relationships"))

        patch_api_contacts_v2_contact_id_body_data = cls(
            type_=type_,
            id=id,
            attributes=attributes,
            relationships=relationships,
        )

        patch_api_contacts_v2_contact_id_body_data.additional_properties = d
        return patch_api_contacts_v2_contact_id_body_data

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
