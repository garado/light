from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetApiPlaylistItemsResponse200IncludedItemAttributes")


@_attrs_define
class GetApiPlaylistItemsResponse200IncludedItemAttributes:
    """
    Attributes:
        bucket (str | Unset):
        content_type (str | Unset):
        key (str | Unset):
        presigned_url (None | str | Unset):
        secret (None | Unset):
        uploaded_at (str | Unset):
        album (str | Unset):
        artist (str | Unset):
        duration (int | Unset):
        title (str | Unset):
    """

    bucket: str | Unset = UNSET
    content_type: str | Unset = UNSET
    key: str | Unset = UNSET
    presigned_url: None | str | Unset = UNSET
    secret: None | Unset = UNSET
    uploaded_at: str | Unset = UNSET
    album: str | Unset = UNSET
    artist: str | Unset = UNSET
    duration: int | Unset = UNSET
    title: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bucket = self.bucket

        content_type = self.content_type

        key = self.key

        presigned_url: None | str | Unset
        if isinstance(self.presigned_url, Unset):
            presigned_url = UNSET
        else:
            presigned_url = self.presigned_url

        secret = self.secret

        uploaded_at = self.uploaded_at

        album = self.album

        artist = self.artist

        duration = self.duration

        title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bucket is not UNSET:
            field_dict["bucket"] = bucket
        if content_type is not UNSET:
            field_dict["content_type"] = content_type
        if key is not UNSET:
            field_dict["key"] = key
        if presigned_url is not UNSET:
            field_dict["presigned_url"] = presigned_url
        if secret is not UNSET:
            field_dict["secret"] = secret
        if uploaded_at is not UNSET:
            field_dict["uploaded_at"] = uploaded_at
        if album is not UNSET:
            field_dict["album"] = album
        if artist is not UNSET:
            field_dict["artist"] = artist
        if duration is not UNSET:
            field_dict["duration"] = duration
        if title is not UNSET:
            field_dict["title"] = title

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        bucket = d.pop("bucket", UNSET)

        content_type = d.pop("content_type", UNSET)

        key = d.pop("key", UNSET)

        def _parse_presigned_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        presigned_url = _parse_presigned_url(d.pop("presigned_url", UNSET))

        secret = d.pop("secret", UNSET)

        uploaded_at = d.pop("uploaded_at", UNSET)

        album = d.pop("album", UNSET)

        artist = d.pop("artist", UNSET)

        duration = d.pop("duration", UNSET)

        title = d.pop("title", UNSET)

        get_api_playlist_items_response_200_included_item_attributes = cls(
            bucket=bucket,
            content_type=content_type,
            key=key,
            presigned_url=presigned_url,
            secret=secret,
            uploaded_at=uploaded_at,
            album=album,
            artist=artist,
            duration=duration,
            title=title,
        )

        get_api_playlist_items_response_200_included_item_attributes.additional_properties = d
        return get_api_playlist_items_response_200_included_item_attributes

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
