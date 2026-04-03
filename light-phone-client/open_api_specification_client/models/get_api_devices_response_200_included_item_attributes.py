from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_api_devices_response_200_included_item_attributes_config import (
        GetApiDevicesResponse200IncludedItemAttributesConfig,
    )


T = TypeVar("T", bound="GetApiDevicesResponse200IncludedItemAttributes")


@_attrs_define
class GetApiDevicesResponse200IncludedItemAttributes:
    """
    Attributes:
        config (GetApiDevicesResponse200IncludedItemAttributesConfig | Unset):
        deleted_at (None | Unset):
        device_id (str | Unset):
        id (str | Unset):
        user_id (str | Unset):
        iccid (str | Unset):
        phone_number (str | Unset):
    """

    config: GetApiDevicesResponse200IncludedItemAttributesConfig | Unset = UNSET
    deleted_at: None | Unset = UNSET
    device_id: str | Unset = UNSET
    id: str | Unset = UNSET
    user_id: str | Unset = UNSET
    iccid: str | Unset = UNSET
    phone_number: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        config: dict[str, Any] | Unset = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        deleted_at = self.deleted_at

        device_id = self.device_id

        id = self.id

        user_id = self.user_id

        iccid = self.iccid

        phone_number = self.phone_number

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if config is not UNSET:
            field_dict["config"] = config
        if deleted_at is not UNSET:
            field_dict["deleted_at"] = deleted_at
        if device_id is not UNSET:
            field_dict["device_id"] = device_id
        if id is not UNSET:
            field_dict["id"] = id
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if iccid is not UNSET:
            field_dict["iccid"] = iccid
        if phone_number is not UNSET:
            field_dict["phone_number"] = phone_number

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_api_devices_response_200_included_item_attributes_config import (
            GetApiDevicesResponse200IncludedItemAttributesConfig,
        )

        d = dict(src_dict)
        _config = d.pop("config", UNSET)
        config: GetApiDevicesResponse200IncludedItemAttributesConfig | Unset
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = GetApiDevicesResponse200IncludedItemAttributesConfig.from_dict(_config)

        deleted_at = d.pop("deleted_at", UNSET)

        device_id = d.pop("device_id", UNSET)

        id = d.pop("id", UNSET)

        user_id = d.pop("user_id", UNSET)

        iccid = d.pop("iccid", UNSET)

        phone_number = d.pop("phone_number", UNSET)

        get_api_devices_response_200_included_item_attributes = cls(
            config=config,
            deleted_at=deleted_at,
            device_id=device_id,
            id=id,
            user_id=user_id,
            iccid=iccid,
            phone_number=phone_number,
        )

        get_api_devices_response_200_included_item_attributes.additional_properties = d
        return get_api_devices_response_200_included_item_attributes

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
