from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetApiNotesParam2Response200DataAttributes")


@_attrs_define
class GetApiNotesParam2Response200DataAttributes:
    """
    Attributes:
        file_id (str | Unset):
        note_type (str | Unset):
        title (str | Unset):
        updated_at (str | Unset):
    """

    file_id: str | Unset = UNSET
    note_type: str | Unset = UNSET
    title: str | Unset = UNSET
    updated_at: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file_id = self.file_id

        note_type = self.note_type

        title = self.title

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if file_id is not UNSET:
            field_dict["file_id"] = file_id
        if note_type is not UNSET:
            field_dict["note_type"] = note_type
        if title is not UNSET:
            field_dict["title"] = title
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        file_id = d.pop("file_id", UNSET)

        note_type = d.pop("note_type", UNSET)

        title = d.pop("title", UNSET)

        updated_at = d.pop("updated_at", UNSET)

        get_api_notes_param_2_response_200_data_attributes = cls(
            file_id=file_id,
            note_type=note_type,
            title=title,
            updated_at=updated_at,
        )

        get_api_notes_param_2_response_200_data_attributes.additional_properties = d
        return get_api_notes_param_2_response_200_data_attributes

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
