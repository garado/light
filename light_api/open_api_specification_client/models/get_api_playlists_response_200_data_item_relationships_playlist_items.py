from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_api_playlists_response_200_data_item_relationships_playlist_items_links import (
        GetApiPlaylistsResponse200DataItemRelationshipsPlaylistItemsLinks,
    )


T = TypeVar("T", bound="GetApiPlaylistsResponse200DataItemRelationshipsPlaylistItems")


@_attrs_define
class GetApiPlaylistsResponse200DataItemRelationshipsPlaylistItems:
    """
    Attributes:
        links (GetApiPlaylistsResponse200DataItemRelationshipsPlaylistItemsLinks):
    """

    links: GetApiPlaylistsResponse200DataItemRelationshipsPlaylistItemsLinks
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        links = self.links.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "links": links,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_api_playlists_response_200_data_item_relationships_playlist_items_links import (
            GetApiPlaylistsResponse200DataItemRelationshipsPlaylistItemsLinks,
        )

        d = dict(src_dict)
        links = GetApiPlaylistsResponse200DataItemRelationshipsPlaylistItemsLinks.from_dict(d.pop("links"))

        get_api_playlists_response_200_data_item_relationships_playlist_items = cls(
            links=links,
        )

        get_api_playlists_response_200_data_item_relationships_playlist_items.additional_properties = d
        return get_api_playlists_response_200_data_item_relationships_playlist_items

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
