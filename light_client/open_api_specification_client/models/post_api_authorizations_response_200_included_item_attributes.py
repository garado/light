from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostApiAuthorizationsResponse200IncludedItemAttributes")


@_attrs_define
class PostApiAuthorizationsResponse200IncludedItemAttributes:
    """
    Attributes:
        token (str | Unset):
        max_age (int | Unset):
    """

    token: str | Unset = UNSET
    max_age: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        token = self.token

        max_age = self.max_age

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if token is not UNSET:
            field_dict["token"] = token
        if max_age is not UNSET:
            field_dict["max_age"] = max_age

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        token = d.pop("token", UNSET)

        max_age = d.pop("max_age", UNSET)

        post_api_authorizations_response_200_included_item_attributes = cls(
            token=token,
            max_age=max_age,
        )

        post_api_authorizations_response_200_included_item_attributes.additional_properties = d
        return post_api_authorizations_response_200_included_item_attributes

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
