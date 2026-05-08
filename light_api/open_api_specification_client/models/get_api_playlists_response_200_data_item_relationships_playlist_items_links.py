from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GetApiPlaylistsResponse200DataItemRelationshipsPlaylistItemsLinks")


@_attrs_define
class GetApiPlaylistsResponse200DataItemRelationshipsPlaylistItemsLinks:
    """
    Attributes:
        related (str):
    """

    related: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        related = self.related

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "related": related,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        related = d.pop("related")

        get_api_playlists_response_200_data_item_relationships_playlist_items_links = cls(
            related=related,
        )

        get_api_playlists_response_200_data_item_relationships_playlist_items_links.additional_properties = d
        return get_api_playlists_response_200_data_item_relationships_playlist_items_links

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
