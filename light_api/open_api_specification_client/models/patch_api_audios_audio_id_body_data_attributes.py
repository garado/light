from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PatchApiAudiosAudioIdBodyDataAttributes")


@_attrs_define
class PatchApiAudiosAudioIdBodyDataAttributes:
    """
    Attributes:
        title (str | Unset):
        artist (str | Unset):
    """

    title: str | Unset = UNSET
    artist: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        artist = self.artist

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if title is not UNSET:
            field_dict["title"] = title
        if artist is not UNSET:
            field_dict["artist"] = artist

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("title", UNSET)

        artist = d.pop("artist", UNSET)

        patch_api_audios_audio_id_body_data_attributes = cls(
            title=title,
            artist=artist,
        )

        patch_api_audios_audio_id_body_data_attributes.additional_properties = d
        return patch_api_audios_audio_id_body_data_attributes

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
