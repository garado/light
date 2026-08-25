from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.patch_api_devices_device_id_developer_mode_body_data_type import (
    PatchApiDevicesDeviceIdDeveloperModeBodyDataType,
)

if TYPE_CHECKING:
    from ..models.patch_api_devices_device_id_developer_mode_body_data_attributes import (
        PatchApiDevicesDeviceIdDeveloperModeBodyDataAttributes,
    )


T = TypeVar("T", bound="PatchApiDevicesDeviceIdDeveloperModeBodyData")


@_attrs_define
class PatchApiDevicesDeviceIdDeveloperModeBodyData:
    """
    Attributes:
        id (str):
        type_ (PatchApiDevicesDeviceIdDeveloperModeBodyDataType):
        attributes (PatchApiDevicesDeviceIdDeveloperModeBodyDataAttributes):
    """

    id: str
    type_: PatchApiDevicesDeviceIdDeveloperModeBodyDataType
    attributes: PatchApiDevicesDeviceIdDeveloperModeBodyDataAttributes
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        type_ = self.type_.value

        attributes = self.attributes.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "type": type_,
                "attributes": attributes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.patch_api_devices_device_id_developer_mode_body_data_attributes import (
            PatchApiDevicesDeviceIdDeveloperModeBodyDataAttributes,
        )

        d = dict(src_dict)
        id = d.pop("id")

        type_ = PatchApiDevicesDeviceIdDeveloperModeBodyDataType(d.pop("type"))

        attributes = PatchApiDevicesDeviceIdDeveloperModeBodyDataAttributes.from_dict(d.pop("attributes"))

        patch_api_devices_device_id_developer_mode_body_data = cls(
            id=id,
            type_=type_,
            attributes=attributes,
        )

        patch_api_devices_device_id_developer_mode_body_data.additional_properties = d
        return patch_api_devices_device_id_developer_mode_body_data

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
