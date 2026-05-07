from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_api_notes_response_200_data_item import GetApiNotesResponse200DataItem
    from ..models.get_api_notes_response_200_included_item import GetApiNotesResponse200IncludedItem
    from ..models.get_api_notes_response_200_jsonapi import GetApiNotesResponse200Jsonapi


T = TypeVar("T", bound="GetApiNotesResponse200")


@_attrs_define
class GetApiNotesResponse200:
    """
    Attributes:
        data (list[GetApiNotesResponse200DataItem]):
        included (list[GetApiNotesResponse200IncludedItem]):
        jsonapi (GetApiNotesResponse200Jsonapi):
    """

    data: list[GetApiNotesResponse200DataItem]
    included: list[GetApiNotesResponse200IncludedItem]
    jsonapi: GetApiNotesResponse200Jsonapi
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        included = []
        for included_item_data in self.included:
            included_item = included_item_data.to_dict()
            included.append(included_item)

        jsonapi = self.jsonapi.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "included": included,
                "jsonapi": jsonapi,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_api_notes_response_200_data_item import GetApiNotesResponse200DataItem
        from ..models.get_api_notes_response_200_included_item import GetApiNotesResponse200IncludedItem
        from ..models.get_api_notes_response_200_jsonapi import GetApiNotesResponse200Jsonapi

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = GetApiNotesResponse200DataItem.from_dict(data_item_data)

            data.append(data_item)

        included = []
        _included = d.pop("included", [])
        for included_item_data in _included:
            included_item = GetApiNotesResponse200IncludedItem.from_dict(included_item_data)

            included.append(included_item)

        jsonapi = GetApiNotesResponse200Jsonapi.from_dict(d.pop("jsonapi"))

        get_api_notes_response_200 = cls(
            data=data,
            included=included,
            jsonapi=jsonapi,
        )

        get_api_notes_response_200.additional_properties = d
        return get_api_notes_response_200

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
