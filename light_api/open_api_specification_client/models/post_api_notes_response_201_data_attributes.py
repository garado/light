from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PostApiNotesResponse201DataAttributes")


@_attrs_define
class PostApiNotesResponse201DataAttributes:
    """
    Attributes:
        device_tool_id (str):
        file_id (str):
        note_type (str):
        title (str):
        updated_at (str):
    """

    device_tool_id: str
    file_id: str
    note_type: str
    title: str
    updated_at: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_tool_id = self.device_tool_id

        file_id = self.file_id

        note_type = self.note_type

        title = self.title

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "device_tool_id": device_tool_id,
                "file_id": file_id,
                "note_type": note_type,
                "title": title,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        device_tool_id = d.pop("device_tool_id")

        file_id = d.pop("file_id")

        note_type = d.pop("note_type")

        title = d.pop("title")

        updated_at = d.pop("updated_at")

        post_api_notes_response_201_data_attributes = cls(
            device_tool_id=device_tool_id,
            file_id=file_id,
            note_type=note_type,
            title=title,
            updated_at=updated_at,
        )

        post_api_notes_response_201_data_attributes.additional_properties = d
        return post_api_notes_response_201_data_attributes

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
