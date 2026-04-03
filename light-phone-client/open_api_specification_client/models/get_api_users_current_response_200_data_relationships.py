from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_api_users_current_response_200_data_relationships_affiliate import (
        GetApiUsersCurrentResponse200DataRelationshipsAffiliate,
    )
    from ..models.get_api_users_current_response_200_data_relationships_subscriptions import (
        GetApiUsersCurrentResponse200DataRelationshipsSubscriptions,
    )


T = TypeVar("T", bound="GetApiUsersCurrentResponse200DataRelationships")


@_attrs_define
class GetApiUsersCurrentResponse200DataRelationships:
    """
    Attributes:
        affiliate (GetApiUsersCurrentResponse200DataRelationshipsAffiliate):
        subscriptions (GetApiUsersCurrentResponse200DataRelationshipsSubscriptions):
    """

    affiliate: GetApiUsersCurrentResponse200DataRelationshipsAffiliate
    subscriptions: GetApiUsersCurrentResponse200DataRelationshipsSubscriptions
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        affiliate = self.affiliate.to_dict()

        subscriptions = self.subscriptions.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "affiliate": affiliate,
                "subscriptions": subscriptions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_api_users_current_response_200_data_relationships_affiliate import (
            GetApiUsersCurrentResponse200DataRelationshipsAffiliate,
        )
        from ..models.get_api_users_current_response_200_data_relationships_subscriptions import (
            GetApiUsersCurrentResponse200DataRelationshipsSubscriptions,
        )

        d = dict(src_dict)
        affiliate = GetApiUsersCurrentResponse200DataRelationshipsAffiliate.from_dict(d.pop("affiliate"))

        subscriptions = GetApiUsersCurrentResponse200DataRelationshipsSubscriptions.from_dict(d.pop("subscriptions"))

        get_api_users_current_response_200_data_relationships = cls(
            affiliate=affiliate,
            subscriptions=subscriptions,
        )

        get_api_users_current_response_200_data_relationships.additional_properties = d
        return get_api_users_current_response_200_data_relationships

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
