from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PostApiAudiosResponse201IncludedItemAttributes")


@_attrs_define
class PostApiAudiosResponse201IncludedItemAttributes:
    """
    Attributes:
        bucket (str):
        content_type (None):
        key (str):
        presigned_url (str):
        secret (None):
        uploaded_at (None):
    """

    bucket: str
    content_type: None
    key: str
    presigned_url: str
    secret: None
    uploaded_at: None
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bucket = self.bucket

        content_type = self.content_type

        key = self.key

        presigned_url = self.presigned_url

        secret = self.secret

        uploaded_at = self.uploaded_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "bucket": bucket,
                "content_type": content_type,
                "key": key,
                "presigned_url": presigned_url,
                "secret": secret,
                "uploaded_at": uploaded_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        bucket = d.pop("bucket")

        content_type = d.pop("content_type")

        key = d.pop("key")

        presigned_url = d.pop("presigned_url")

        secret = d.pop("secret")

        uploaded_at = d.pop("uploaded_at")

        post_api_audios_response_201_included_item_attributes = cls(
            bucket=bucket,
            content_type=content_type,
            key=key,
            presigned_url=presigned_url,
            secret=secret,
            uploaded_at=uploaded_at,
        )

        post_api_audios_response_201_included_item_attributes.additional_properties = d
        return post_api_audios_response_201_included_item_attributes

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
