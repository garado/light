from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GetApiPlaylistItemsResponse200DataItemAttributes")


@_attrs_define
class GetApiPlaylistItemsResponse200DataItemAttributes:
    """
    Attributes:
        audio_id (str):
        playlist_id (str):
        position (int):
    """

    audio_id: str
    playlist_id: str
    position: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        audio_id = self.audio_id

        playlist_id = self.playlist_id

        position = self.position

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "audio_id": audio_id,
                "playlist_id": playlist_id,
                "position": position,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        audio_id = d.pop("audio_id")

        playlist_id = d.pop("playlist_id")

        position = d.pop("position")

        get_api_playlist_items_response_200_data_item_attributes = cls(
            audio_id=audio_id,
            playlist_id=playlist_id,
            position=position,
        )

        get_api_playlist_items_response_200_data_item_attributes.additional_properties = d
        return get_api_playlist_items_response_200_data_item_attributes

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
