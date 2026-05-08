from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_api_playlist_items_response_200_data_item import GetApiPlaylistItemsResponse200DataItem
    from ..models.get_api_playlist_items_response_200_included_item import GetApiPlaylistItemsResponse200IncludedItem
    from ..models.get_api_playlist_items_response_200_jsonapi import GetApiPlaylistItemsResponse200Jsonapi


T = TypeVar("T", bound="GetApiPlaylistItemsResponse200")


@_attrs_define
class GetApiPlaylistItemsResponse200:
    """
    Attributes:
        data (list[GetApiPlaylistItemsResponse200DataItem]):
        jsonapi (GetApiPlaylistItemsResponse200Jsonapi):
        included (list[GetApiPlaylistItemsResponse200IncludedItem] | Unset):
    """

    data: list[GetApiPlaylistItemsResponse200DataItem]
    jsonapi: GetApiPlaylistItemsResponse200Jsonapi
    included: list[GetApiPlaylistItemsResponse200IncludedItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        jsonapi = self.jsonapi.to_dict()

        included: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.included, Unset):
            included = []
            for included_item_data in self.included:
                included_item = included_item_data.to_dict()
                included.append(included_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "jsonapi": jsonapi,
            }
        )
        if included is not UNSET:
            field_dict["included"] = included

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_api_playlist_items_response_200_data_item import GetApiPlaylistItemsResponse200DataItem
        from ..models.get_api_playlist_items_response_200_included_item import (
            GetApiPlaylistItemsResponse200IncludedItem,
        )
        from ..models.get_api_playlist_items_response_200_jsonapi import GetApiPlaylistItemsResponse200Jsonapi

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = GetApiPlaylistItemsResponse200DataItem.from_dict(data_item_data)

            data.append(data_item)

        jsonapi = GetApiPlaylistItemsResponse200Jsonapi.from_dict(d.pop("jsonapi"))

        _included = d.pop("included", UNSET)
        included: list[GetApiPlaylistItemsResponse200IncludedItem] | Unset = UNSET
        if _included is not UNSET:
            included = []
            for included_item_data in _included:
                included_item = GetApiPlaylistItemsResponse200IncludedItem.from_dict(included_item_data)

                included.append(included_item)

        get_api_playlist_items_response_200 = cls(
            data=data,
            jsonapi=jsonapi,
            included=included,
        )

        get_api_playlist_items_response_200.additional_properties = d
        return get_api_playlist_items_response_200

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
