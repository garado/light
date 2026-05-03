from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GetApiDevicesResponse200IncludedItemAttributesConfigAddress")


@_attrs_define
class GetApiDevicesResponse200IncludedItemAttributesConfigAddress:
    """
    Attributes:
        city (str):
        country_code (str):
        country_name (str):
        county (str):
        label (str):
        postal_code (str):
        state (str):
        state_code (str):
    """

    city: str
    country_code: str
    country_name: str
    county: str
    label: str
    postal_code: str
    state: str
    state_code: str
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
        field_dict.update(
            {
                "city": city,
                "countryCode": country_code,
                "countryName": country_name,
                "county": county,
                "label": label,
                "postalCode": postal_code,
                "state": state,
                "stateCode": state_code,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        city = d.pop("city")

        country_code = d.pop("countryCode")

        country_name = d.pop("countryName")

        county = d.pop("county")

        label = d.pop("label")

        postal_code = d.pop("postalCode")

        state = d.pop("state")

        state_code = d.pop("stateCode")

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
