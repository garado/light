from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.patch_api_notes_note_id_body_data_relationships_file import (
        PatchApiNotesNoteIdBodyDataRelationshipsFile,
    )


T = TypeVar("T", bound="PatchApiNotesNoteIdBodyDataRelationships")


@_attrs_define
class PatchApiNotesNoteIdBodyDataRelationships:
    """
    Attributes:
        file (PatchApiNotesNoteIdBodyDataRelationshipsFile | Unset):
    """

    file: PatchApiNotesNoteIdBodyDataRelationshipsFile | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file: dict[str, Any] | Unset = UNSET
        if not isinstance(self.file, Unset):
            file = self.file.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if file is not UNSET:
            field_dict["file"] = file

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.patch_api_notes_note_id_body_data_relationships_file import (
            PatchApiNotesNoteIdBodyDataRelationshipsFile,
        )

        d = dict(src_dict)
        _file = d.pop("file", UNSET)
        file: PatchApiNotesNoteIdBodyDataRelationshipsFile | Unset
        if isinstance(_file, Unset):
            file = UNSET
        else:
            file = PatchApiNotesNoteIdBodyDataRelationshipsFile.from_dict(_file)

        patch_api_notes_note_id_body_data_relationships = cls(
            file=file,
        )

        patch_api_notes_note_id_body_data_relationships.additional_properties = d
        return patch_api_notes_note_id_body_data_relationships

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
