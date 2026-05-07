from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostApiAuthorizationsResponse200DataAttributes")


@_attrs_define
class PostApiAuthorizationsResponse200DataAttributes:
    """
    Attributes:
        email (str | Unset):
        given_name (str | Unset):
        family_name (str | Unset):
    """

    email: str | Unset = UNSET
    given_name: str | Unset = UNSET
    family_name: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        given_name = self.given_name

        family_name = self.family_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if email is not UNSET:
            field_dict["email"] = email
        if given_name is not UNSET:
            field_dict["given_name"] = given_name
        if family_name is not UNSET:
            field_dict["family_name"] = family_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email", UNSET)

        given_name = d.pop("given_name", UNSET)

        family_name = d.pop("family_name", UNSET)

        post_api_authorizations_response_200_data_attributes = cls(
            email=email,
            given_name=given_name,
            family_name=family_name,
        )

        post_api_authorizations_response_200_data_attributes.additional_properties = d
        return post_api_authorizations_response_200_data_attributes

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
