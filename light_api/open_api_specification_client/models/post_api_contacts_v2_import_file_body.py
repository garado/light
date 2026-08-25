from __future__ import annotations

from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..types import File

T = TypeVar("T", bound="PostApiContactsV2ImportFileBody")


@_attrs_define
class PostApiContactsV2ImportFileBody:
    """
    Attributes:
        device_id (str):
        content_type (str):
        file (File):
    """

    device_id: str
    content_type: str
    file: File
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_id = self.device_id

        content_type = self.content_type

        file = self.file.to_tuple()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "device_id": device_id,
                "Content-Type": content_type,
                "file": file,
            }
        )

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        files.append(("device_id", (None, str(self.device_id).encode(), "text/plain")))

        files.append(("Content-Type", (None, str(self.content_type).encode(), "text/plain")))

        files.append(("file", self.file.to_tuple()))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        device_id = d.pop("device_id")

        content_type = d.pop("Content-Type")

        file = File(payload=BytesIO(d.pop("file")))

        post_api_contacts_v2_import_file_body = cls(
            device_id=device_id,
            content_type=content_type,
            file=file,
        )

        post_api_contacts_v2_import_file_body.additional_properties = d
        return post_api_contacts_v2_import_file_body

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
