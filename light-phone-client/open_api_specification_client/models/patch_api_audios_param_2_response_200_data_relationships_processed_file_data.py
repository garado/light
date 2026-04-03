from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PatchApiAudiosParam2Response200DataRelationshipsProcessedFileData")


@_attrs_define
class PatchApiAudiosParam2Response200DataRelationshipsProcessedFileData:
    """
    Attributes:
        id (str):
        type_ (str):
    """

    id: str
    type_: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "type": type_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        type_ = d.pop("type")

        patch_api_audios_param_2_response_200_data_relationships_processed_file_data = cls(
            id=id,
            type_=type_,
        )

        patch_api_audios_param_2_response_200_data_relationships_processed_file_data.additional_properties = d
        return patch_api_audios_param_2_response_200_data_relationships_processed_file_data

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
