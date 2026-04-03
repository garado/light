from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.post_api_notes_body_data_attributes_note_type import PostApiNotesBodyDataAttributesNoteType

T = TypeVar("T", bound="PostApiNotesBodyDataAttributes")


@_attrs_define
class PostApiNotesBodyDataAttributes:
    """
    Attributes:
        device_tool_id (str):
        filename (str):
        note_type (PostApiNotesBodyDataAttributesNoteType):
        title (str):
    """

    device_tool_id: str
    filename: str
    note_type: PostApiNotesBodyDataAttributesNoteType
    title: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_tool_id = self.device_tool_id

        filename = self.filename

        note_type = self.note_type.value

        title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "device_tool_id": device_tool_id,
                "filename": filename,
                "note_type": note_type,
                "title": title,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        device_tool_id = d.pop("device_tool_id")

        filename = d.pop("filename")

        note_type = PostApiNotesBodyDataAttributesNoteType(d.pop("note_type"))

        title = d.pop("title")

        post_api_notes_body_data_attributes = cls(
            device_tool_id=device_tool_id,
            filename=filename,
            note_type=note_type,
            title=title,
        )

        post_api_notes_body_data_attributes.additional_properties = d
        return post_api_notes_body_data_attributes

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
