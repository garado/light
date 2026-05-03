from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GetApiUsersCurrentResponse200DataAttributes")


@_attrs_define
class GetApiUsersCurrentResponse200DataAttributes:
    """
    Attributes:
        email (str):
        family_name (str):
        given_name (str):
        phone_contact (None):
        roles (list[Any]):
    """

    email: str
    family_name: str
    given_name: str
    phone_contact: None
    roles: list[Any]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        family_name = self.family_name

        given_name = self.given_name

        phone_contact = self.phone_contact

        roles = self.roles

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "family_name": family_name,
                "given_name": given_name,
                "phone_contact": phone_contact,
                "roles": roles,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        family_name = d.pop("family_name")

        given_name = d.pop("given_name")

        phone_contact = d.pop("phone_contact")

        roles = cast(list[Any], d.pop("roles"))

        get_api_users_current_response_200_data_attributes = cls(
            email=email,
            family_name=family_name,
            given_name=given_name,
            phone_contact=phone_contact,
            roles=roles,
        )

        get_api_users_current_response_200_data_attributes.additional_properties = d
        return get_api_users_current_response_200_data_attributes

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
