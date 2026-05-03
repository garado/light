from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PatchApiPlaylistItemsParam2Response200DataAttributes")


@_attrs_define
class PatchApiPlaylistItemsParam2Response200DataAttributes:
    """
    Attributes:
        album (None):
        artist (None):
        duration (None):
        title (None):
    """

    album: None
    artist: None
    duration: None
    title: None
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        album = self.album

        artist = self.artist

        duration = self.duration

        title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "album": album,
                "artist": artist,
                "duration": duration,
                "title": title,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        album = d.pop("album")

        artist = d.pop("artist")

        duration = d.pop("duration")

        title = d.pop("title")

        patch_api_playlist_items_param_2_response_200_data_attributes = cls(
            album=album,
            artist=artist,
            duration=duration,
            title=title,
        )

        patch_api_playlist_items_param_2_response_200_data_attributes.additional_properties = d
        return patch_api_playlist_items_param_2_response_200_data_attributes

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
