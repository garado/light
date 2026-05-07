from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_api_authorizations_response_200_data import PostApiAuthorizationsResponse200Data
    from ..models.post_api_authorizations_response_200_included_item import PostApiAuthorizationsResponse200IncludedItem


T = TypeVar("T", bound="PostApiAuthorizationsResponse200")


@_attrs_define
class PostApiAuthorizationsResponse200:
    """
    Attributes:
        data (PostApiAuthorizationsResponse200Data | Unset):
        included (list[PostApiAuthorizationsResponse200IncludedItem] | Unset):
    """

    data: PostApiAuthorizationsResponse200Data | Unset = UNSET
    included: list[PostApiAuthorizationsResponse200IncludedItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.data, Unset):
            data = self.data.to_dict()

        included: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.included, Unset):
            included = []
            for included_item_data in self.included:
                included_item = included_item_data.to_dict()
                included.append(included_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if data is not UNSET:
            field_dict["data"] = data
        if included is not UNSET:
            field_dict["included"] = included

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_api_authorizations_response_200_data import PostApiAuthorizationsResponse200Data
        from ..models.post_api_authorizations_response_200_included_item import (
            PostApiAuthorizationsResponse200IncludedItem,
        )

        d = dict(src_dict)
        _data = d.pop("data", UNSET)
        data: PostApiAuthorizationsResponse200Data | Unset
        if isinstance(_data, Unset):
            data = UNSET
        else:
            data = PostApiAuthorizationsResponse200Data.from_dict(_data)

        _included = d.pop("included", UNSET)
        included: list[PostApiAuthorizationsResponse200IncludedItem] | Unset = UNSET
        if _included is not UNSET:
            included = []
            for included_item_data in _included:
                included_item = PostApiAuthorizationsResponse200IncludedItem.from_dict(included_item_data)

                included.append(included_item)

        post_api_authorizations_response_200 = cls(
            data=data,
            included=included,
        )

        post_api_authorizations_response_200.additional_properties = d
        return post_api_authorizations_response_200

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
