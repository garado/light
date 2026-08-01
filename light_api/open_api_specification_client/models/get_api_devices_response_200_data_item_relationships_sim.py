from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_api_devices_response_200_data_item_relationships_sim_data import (
        GetApiDevicesResponse200DataItemRelationshipsSimData,
    )


T = TypeVar("T", bound="GetApiDevicesResponse200DataItemRelationshipsSim")


@_attrs_define
class GetApiDevicesResponse200DataItemRelationshipsSim:
    """
    Attributes:
        data (GetApiDevicesResponse200DataItemRelationshipsSimData | None):
    """

    data: GetApiDevicesResponse200DataItemRelationshipsSimData | None
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = self.data.to_dict() if self.data is not None else None

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_api_devices_response_200_data_item_relationships_sim_data import (
            GetApiDevicesResponse200DataItemRelationshipsSimData,
        )

        d = dict(src_dict)
        _data = d.pop("data")
        data = (
            GetApiDevicesResponse200DataItemRelationshipsSimData.from_dict(_data)
            if _data is not None
            else None
        )

        get_api_devices_response_200_data_item_relationships_sim = cls(
            data=data,
        )

        get_api_devices_response_200_data_item_relationships_sim.additional_properties = d
        return get_api_devices_response_200_data_item_relationships_sim

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
