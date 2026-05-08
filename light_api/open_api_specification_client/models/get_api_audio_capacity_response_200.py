from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GetApiAudioCapacityResponse200")


@_attrs_define
class GetApiAudioCapacityResponse200:
    """
    Attributes:
        processing_count (int):
        failed_count (int):
        remaining_capacity (int):
        total_capacity (int):
    """

    processing_count: int
    failed_count: int
    remaining_capacity: int
    total_capacity: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        processing_count = self.processing_count

        failed_count = self.failed_count

        remaining_capacity = self.remaining_capacity

        total_capacity = self.total_capacity

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "processing_count": processing_count,
                "failed_count": failed_count,
                "remaining_capacity": remaining_capacity,
                "total_capacity": total_capacity,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        processing_count = d.pop("processing_count")

        failed_count = d.pop("failed_count")

        remaining_capacity = d.pop("remaining_capacity")

        total_capacity = d.pop("total_capacity")

        get_api_audio_capacity_response_200 = cls(
            processing_count=processing_count,
            failed_count=failed_count,
            remaining_capacity=remaining_capacity,
            total_capacity=total_capacity,
        )

        get_api_audio_capacity_response_200.additional_properties = d
        return get_api_audio_capacity_response_200

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
