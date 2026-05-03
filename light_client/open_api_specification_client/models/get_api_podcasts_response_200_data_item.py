from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_api_podcasts_response_200_data_item_attributes import GetApiPodcastsResponse200DataItemAttributes


T = TypeVar("T", bound="GetApiPodcastsResponse200DataItem")


@_attrs_define
class GetApiPodcastsResponse200DataItem:
    """
    Attributes:
        attributes (GetApiPodcastsResponse200DataItemAttributes):
        id (str):
        type_ (str):
    """

    attributes: GetApiPodcastsResponse200DataItemAttributes
    id: str
    type_: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        attributes = self.attributes.to_dict()

        id = self.id

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "attributes": attributes,
                "id": id,
                "type": type_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_api_podcasts_response_200_data_item_attributes import (
            GetApiPodcastsResponse200DataItemAttributes,
        )

        d = dict(src_dict)
        attributes = GetApiPodcastsResponse200DataItemAttributes.from_dict(d.pop("attributes"))

        id = d.pop("id")

        type_ = d.pop("type")

        get_api_podcasts_response_200_data_item = cls(
            attributes=attributes,
            id=id,
            type_=type_,
        )

        get_api_podcasts_response_200_data_item.additional_properties = d
        return get_api_podcasts_response_200_data_item

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
