from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_api_playlist_items_response_200_included_item_relationships_processed_file_data import (
        GetApiPlaylistItemsResponse200IncludedItemRelationshipsProcessedFileData,
    )


T = TypeVar("T", bound="GetApiPlaylistItemsResponse200IncludedItemRelationshipsProcessedFile")


@_attrs_define
class GetApiPlaylistItemsResponse200IncludedItemRelationshipsProcessedFile:
    """
    Attributes:
        data (GetApiPlaylistItemsResponse200IncludedItemRelationshipsProcessedFileData):
    """

    data: GetApiPlaylistItemsResponse200IncludedItemRelationshipsProcessedFileData
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = self.data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_api_playlist_items_response_200_included_item_relationships_processed_file_data import (
            GetApiPlaylistItemsResponse200IncludedItemRelationshipsProcessedFileData,
        )

        d = dict(src_dict)
        data = GetApiPlaylistItemsResponse200IncludedItemRelationshipsProcessedFileData.from_dict(d.pop("data"))

        get_api_playlist_items_response_200_included_item_relationships_processed_file = cls(
            data=data,
        )

        get_api_playlist_items_response_200_included_item_relationships_processed_file.additional_properties = d
        return get_api_playlist_items_response_200_included_item_relationships_processed_file

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
