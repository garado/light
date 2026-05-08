from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PatchApiNotesNoteIdBodyDataAttributes")


@_attrs_define
class PatchApiNotesNoteIdBodyDataAttributes:
    """
    Attributes:
        title (str | Unset):
        updated_at (str | Unset):
        note_type (str | Unset):
    """

    title: str | Unset = UNSET
    updated_at: str | Unset = UNSET
    note_type: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        updated_at = self.updated_at

        note_type = self.note_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if title is not UNSET:
            field_dict["title"] = title
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if note_type is not UNSET:
            field_dict["note_type"] = note_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("title", UNSET)

        updated_at = d.pop("updated_at", UNSET)

        note_type = d.pop("note_type", UNSET)

        patch_api_notes_note_id_body_data_attributes = cls(
            title=title,
            updated_at=updated_at,
            note_type=note_type,
        )

        patch_api_notes_note_id_body_data_attributes.additional_properties = d
        return patch_api_notes_note_id_body_data_attributes

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
