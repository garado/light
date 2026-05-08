from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.patch_api_audios_audio_id_response_200_data import PatchApiAudiosAudioIdResponse200Data
    from ..models.patch_api_audios_audio_id_response_200_included_item import (
        PatchApiAudiosAudioIdResponse200IncludedItem,
    )
    from ..models.patch_api_audios_audio_id_response_200_jsonapi import PatchApiAudiosAudioIdResponse200Jsonapi


T = TypeVar("T", bound="PatchApiAudiosAudioIdResponse200")


@_attrs_define
class PatchApiAudiosAudioIdResponse200:
    """
    Attributes:
        data (PatchApiAudiosAudioIdResponse200Data):
        included (list[PatchApiAudiosAudioIdResponse200IncludedItem]):
        jsonapi (PatchApiAudiosAudioIdResponse200Jsonapi):
    """

    data: PatchApiAudiosAudioIdResponse200Data
    included: list[PatchApiAudiosAudioIdResponse200IncludedItem]
    jsonapi: PatchApiAudiosAudioIdResponse200Jsonapi
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = self.data.to_dict()

        included = []
        for included_item_data in self.included:
            included_item = included_item_data.to_dict()
            included.append(included_item)

        jsonapi = self.jsonapi.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "included": included,
                "jsonapi": jsonapi,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.patch_api_audios_audio_id_response_200_data import PatchApiAudiosAudioIdResponse200Data
        from ..models.patch_api_audios_audio_id_response_200_included_item import (
            PatchApiAudiosAudioIdResponse200IncludedItem,
        )
        from ..models.patch_api_audios_audio_id_response_200_jsonapi import PatchApiAudiosAudioIdResponse200Jsonapi

        d = dict(src_dict)
        data = PatchApiAudiosAudioIdResponse200Data.from_dict(d.pop("data"))

        included = []
        _included = d.pop("included")
        for included_item_data in _included:
            included_item = PatchApiAudiosAudioIdResponse200IncludedItem.from_dict(included_item_data)

            included.append(included_item)

        jsonapi = PatchApiAudiosAudioIdResponse200Jsonapi.from_dict(d.pop("jsonapi"))

        patch_api_audios_audio_id_response_200 = cls(
            data=data,
            included=included,
            jsonapi=jsonapi,
        )

        patch_api_audios_audio_id_response_200.additional_properties = d
        return patch_api_audios_audio_id_response_200

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
