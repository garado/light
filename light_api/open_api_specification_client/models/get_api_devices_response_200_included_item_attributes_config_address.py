from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetApiDevicesResponse200IncludedItemAttributesConfigAddress")


@_attrs_define
class GetApiDevicesResponse200IncludedItemAttributesConfigAddress:
    """
    Attributes:
        city (str | Unset):
        country_code (str | Unset):
        country_name (str | Unset):
        county (str | Unset):
        label (str | Unset):
        postal_code (str | Unset):
        state (str | Unset):
        state_code (str | Unset):
    """

    city: str | Unset = UNSET
    country_code: str | Unset = UNSET
    country_name: str | Unset = UNSET
    county: str | Unset = UNSET
    label: str | Unset = UNSET
    postal_code: str | Unset = UNSET
    state: str | Unset = UNSET
    state_code: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        city = self.city

        country_code = self.country_code

        country_name = self.country_name

        county = self.county

        label = self.label

        postal_code = self.postal_code

        state = self.state

        state_code = self.state_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        if city is not UNSET:
            field_dict["city"] = city
        if country_code is not UNSET:
            field_dict["countryCode"] = country_code
        if country_name is not UNSET:
            field_dict["countryName"] = country_name
        if county is not UNSET:
            field_dict["county"] = county
        if label is not UNSET:
            field_dict["label"] = label
        if postal_code is not UNSET:
            field_dict["postalCode"] = postal_code
        if state is not UNSET:
            field_dict["state"] = state
        if state_code is not UNSET:
            field_dict["stateCode"] = state_code

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        city = d.pop("city", UNSET)

        country_code = d.pop("countryCode", UNSET)

        country_name = d.pop("countryName", UNSET)

        county = d.pop("county", UNSET)

        label = d.pop("label", UNSET)

        postal_code = d.pop("postalCode", UNSET)

        state = d.pop("state", UNSET)

        state_code = d.pop("stateCode", UNSET)

        get_api_devices_response_200_included_item_attributes_config_address = cls(
            city=city,
            country_code=country_code,
            country_name=country_name,
            county=county,
            label=label,
            postal_code=postal_code,
            state=state,
            state_code=state_code,
        )

        get_api_devices_response_200_included_item_attributes_config_address.additional_properties = d
        return get_api_devices_response_200_included_item_attributes_config_address

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
