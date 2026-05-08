from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetApiNotesNoteIdGeneratePresignedPutUrlResponse200")


@_attrs_define
class GetApiNotesNoteIdGeneratePresignedPutUrlResponse200:
    """
    Attributes:
        presigned_put_url (str | Unset):
    """

    presigned_put_url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        presigned_put_url = self.presigned_put_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if presigned_put_url is not UNSET:
            field_dict["presigned_put_url"] = presigned_put_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        presigned_put_url = d.pop("presigned_put_url", UNSET)

        get_api_notes_note_id_generate_presigned_put_url_response_200 = cls(
            presigned_put_url=presigned_put_url,
        )

        get_api_notes_note_id_generate_presigned_put_url_response_200.additional_properties = d
        return get_api_notes_note_id_generate_presigned_put_url_response_200

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
