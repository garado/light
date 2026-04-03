from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.post_api_playlists_sort_mode_body_sort_mode import PostApiPlaylistsSortModeBodySortMode

T = TypeVar("T", bound="PostApiPlaylistsSortModeBody")


@_attrs_define
class PostApiPlaylistsSortModeBody:
    """
    Attributes:
        playlist_id (str):
        device_tool_id (str):
        sort_mode (PostApiPlaylistsSortModeBodySortMode): Native API sort modes. Note: artists_asc and artists_desc
            appear inverted in the API response.
    """

    playlist_id: str
    device_tool_id: str
    sort_mode: PostApiPlaylistsSortModeBodySortMode
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        playlist_id = self.playlist_id

        device_tool_id = self.device_tool_id

        sort_mode = self.sort_mode.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "playlist_id": playlist_id,
                "device_tool_id": device_tool_id,
                "sort_mode": sort_mode,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        playlist_id = d.pop("playlist_id")

        device_tool_id = d.pop("device_tool_id")

        sort_mode = PostApiPlaylistsSortModeBodySortMode(d.pop("sort_mode"))

        post_api_playlists_sort_mode_body = cls(
            playlist_id=playlist_id,
            device_tool_id=device_tool_id,
            sort_mode=sort_mode,
        )

        post_api_playlists_sort_mode_body.additional_properties = d
        return post_api_playlists_sort_mode_body

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
