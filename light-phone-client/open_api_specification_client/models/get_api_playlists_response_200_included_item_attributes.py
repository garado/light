from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_api_playlists_response_200_included_item_attributes_config import (
        GetApiPlaylistsResponse200IncludedItemAttributesConfig,
    )


T = TypeVar("T", bound="GetApiPlaylistsResponse200IncludedItemAttributes")


@_attrs_define
class GetApiPlaylistsResponse200IncludedItemAttributes:
    """
    Attributes:
        email (str | Unset):
        family_name (str | Unset):
        given_name (str | Unset):
        phone_contact (None | Unset):
        roles (list[Any] | Unset):
        config (GetApiPlaylistsResponse200IncludedItemAttributesConfig | Unset):
        deleted_at (None | Unset):
    """

    email: str | Unset = UNSET
    family_name: str | Unset = UNSET
    given_name: str | Unset = UNSET
    phone_contact: None | Unset = UNSET
    roles: list[Any] | Unset = UNSET
    config: GetApiPlaylistsResponse200IncludedItemAttributesConfig | Unset = UNSET
    deleted_at: None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        family_name = self.family_name

        given_name = self.given_name

        phone_contact = self.phone_contact

        roles: list[Any] | Unset = UNSET
        if not isinstance(self.roles, Unset):
            roles = self.roles

        config: dict[str, Any] | Unset = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        deleted_at = self.deleted_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if email is not UNSET:
            field_dict["email"] = email
        if family_name is not UNSET:
            field_dict["family_name"] = family_name
        if given_name is not UNSET:
            field_dict["given_name"] = given_name
        if phone_contact is not UNSET:
            field_dict["phone_contact"] = phone_contact
        if roles is not UNSET:
            field_dict["roles"] = roles
        if config is not UNSET:
            field_dict["config"] = config
        if deleted_at is not UNSET:
            field_dict["deleted_at"] = deleted_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_api_playlists_response_200_included_item_attributes_config import (
            GetApiPlaylistsResponse200IncludedItemAttributesConfig,
        )

        d = dict(src_dict)
        email = d.pop("email", UNSET)

        family_name = d.pop("family_name", UNSET)

        given_name = d.pop("given_name", UNSET)

        phone_contact = d.pop("phone_contact", UNSET)

        roles = cast(list[Any], d.pop("roles", UNSET))

        _config = d.pop("config", UNSET)
        config: GetApiPlaylistsResponse200IncludedItemAttributesConfig | Unset
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = GetApiPlaylistsResponse200IncludedItemAttributesConfig.from_dict(_config)

        deleted_at = d.pop("deleted_at", UNSET)

        get_api_playlists_response_200_included_item_attributes = cls(
            email=email,
            family_name=family_name,
            given_name=given_name,
            phone_contact=phone_contact,
            roles=roles,
            config=config,
            deleted_at=deleted_at,
        )

        get_api_playlists_response_200_included_item_attributes.additional_properties = d
        return get_api_playlists_response_200_included_item_attributes

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
