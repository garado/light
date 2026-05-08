from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_api_playlists_response_200_data_item_relationships_device_tool import (
        GetApiPlaylistsResponse200DataItemRelationshipsDeviceTool,
    )
    from ..models.get_api_playlists_response_200_data_item_relationships_playlist_items import (
        GetApiPlaylistsResponse200DataItemRelationshipsPlaylistItems,
    )
    from ..models.get_api_playlists_response_200_data_item_relationships_user import (
        GetApiPlaylistsResponse200DataItemRelationshipsUser,
    )


T = TypeVar("T", bound="GetApiPlaylistsResponse200DataItemRelationships")


@_attrs_define
class GetApiPlaylistsResponse200DataItemRelationships:
    """
    Attributes:
        device_tool (GetApiPlaylistsResponse200DataItemRelationshipsDeviceTool):
        playlist_items (GetApiPlaylistsResponse200DataItemRelationshipsPlaylistItems):
        user (GetApiPlaylistsResponse200DataItemRelationshipsUser):
    """

    device_tool: GetApiPlaylistsResponse200DataItemRelationshipsDeviceTool
    playlist_items: GetApiPlaylistsResponse200DataItemRelationshipsPlaylistItems
    user: GetApiPlaylistsResponse200DataItemRelationshipsUser
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_tool = self.device_tool.to_dict()

        playlist_items = self.playlist_items.to_dict()

        user = self.user.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "device_tool": device_tool,
                "playlist_items": playlist_items,
                "user": user,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_api_playlists_response_200_data_item_relationships_device_tool import (
            GetApiPlaylistsResponse200DataItemRelationshipsDeviceTool,
        )
        from ..models.get_api_playlists_response_200_data_item_relationships_playlist_items import (
            GetApiPlaylistsResponse200DataItemRelationshipsPlaylistItems,
        )
        from ..models.get_api_playlists_response_200_data_item_relationships_user import (
            GetApiPlaylistsResponse200DataItemRelationshipsUser,
        )

        d = dict(src_dict)
        device_tool = GetApiPlaylistsResponse200DataItemRelationshipsDeviceTool.from_dict(d.pop("device_tool"))

        playlist_items = GetApiPlaylistsResponse200DataItemRelationshipsPlaylistItems.from_dict(d.pop("playlist_items"))

        user = GetApiPlaylistsResponse200DataItemRelationshipsUser.from_dict(d.pop("user"))

        get_api_playlists_response_200_data_item_relationships = cls(
            device_tool=device_tool,
            playlist_items=playlist_items,
            user=user,
        )

        get_api_playlists_response_200_data_item_relationships.additional_properties = d
        return get_api_playlists_response_200_data_item_relationships

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
