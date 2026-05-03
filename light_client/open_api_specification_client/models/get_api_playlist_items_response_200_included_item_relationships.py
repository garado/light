from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_api_playlist_items_response_200_included_item_relationships_processed_file import (
        GetApiPlaylistItemsResponse200IncludedItemRelationshipsProcessedFile,
    )
    from ..models.get_api_playlist_items_response_200_included_item_relationships_raw_file import (
        GetApiPlaylistItemsResponse200IncludedItemRelationshipsRawFile,
    )


T = TypeVar("T", bound="GetApiPlaylistItemsResponse200IncludedItemRelationships")


@_attrs_define
class GetApiPlaylistItemsResponse200IncludedItemRelationships:
    """
    Attributes:
        processed_file (GetApiPlaylistItemsResponse200IncludedItemRelationshipsProcessedFile):
        raw_file (GetApiPlaylistItemsResponse200IncludedItemRelationshipsRawFile):
    """

    processed_file: GetApiPlaylistItemsResponse200IncludedItemRelationshipsProcessedFile
    raw_file: GetApiPlaylistItemsResponse200IncludedItemRelationshipsRawFile
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        processed_file = self.processed_file.to_dict()

        raw_file = self.raw_file.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "processed_file": processed_file,
                "raw_file": raw_file,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_api_playlist_items_response_200_included_item_relationships_processed_file import (
            GetApiPlaylistItemsResponse200IncludedItemRelationshipsProcessedFile,
        )
        from ..models.get_api_playlist_items_response_200_included_item_relationships_raw_file import (
            GetApiPlaylistItemsResponse200IncludedItemRelationshipsRawFile,
        )

        d = dict(src_dict)
        processed_file = GetApiPlaylistItemsResponse200IncludedItemRelationshipsProcessedFile.from_dict(
            d.pop("processed_file")
        )

        raw_file = GetApiPlaylistItemsResponse200IncludedItemRelationshipsRawFile.from_dict(d.pop("raw_file"))

        get_api_playlist_items_response_200_included_item_relationships = cls(
            processed_file=processed_file,
            raw_file=raw_file,
        )

        get_api_playlist_items_response_200_included_item_relationships.additional_properties = d
        return get_api_playlist_items_response_200_included_item_relationships

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
