from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.patch_api_playlist_items_playlist_item_id_response_200_data import (
        PatchApiPlaylistItemsPlaylistItemIdResponse200Data,
    )
    from ..models.patch_api_playlist_items_playlist_item_id_response_200_jsonapi import (
        PatchApiPlaylistItemsPlaylistItemIdResponse200Jsonapi,
    )


T = TypeVar("T", bound="PatchApiPlaylistItemsPlaylistItemIdResponse200")


@_attrs_define
class PatchApiPlaylistItemsPlaylistItemIdResponse200:
    """
    Attributes:
        data (PatchApiPlaylistItemsPlaylistItemIdResponse200Data):
        jsonapi (PatchApiPlaylistItemsPlaylistItemIdResponse200Jsonapi):
    """

    data: PatchApiPlaylistItemsPlaylistItemIdResponse200Data
    jsonapi: PatchApiPlaylistItemsPlaylistItemIdResponse200Jsonapi
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = self.data.to_dict()

        jsonapi = self.jsonapi.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "jsonapi": jsonapi,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.patch_api_playlist_items_playlist_item_id_response_200_data import (
            PatchApiPlaylistItemsPlaylistItemIdResponse200Data,
        )
        from ..models.patch_api_playlist_items_playlist_item_id_response_200_jsonapi import (
            PatchApiPlaylistItemsPlaylistItemIdResponse200Jsonapi,
        )

        d = dict(src_dict)
        data = PatchApiPlaylistItemsPlaylistItemIdResponse200Data.from_dict(d.pop("data"))

        jsonapi = PatchApiPlaylistItemsPlaylistItemIdResponse200Jsonapi.from_dict(d.pop("jsonapi"))

        patch_api_playlist_items_playlist_item_id_response_200 = cls(
            data=data,
            jsonapi=jsonapi,
        )

        patch_api_playlist_items_playlist_item_id_response_200.additional_properties = d
        return patch_api_playlist_items_playlist_item_id_response_200

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
