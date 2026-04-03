from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_api_playlists_response_200_data_item_relationships_user_data import (
        GetApiPlaylistsResponse200DataItemRelationshipsUserData,
    )


T = TypeVar("T", bound="GetApiPlaylistsResponse200DataItemRelationshipsUser")


@_attrs_define
class GetApiPlaylistsResponse200DataItemRelationshipsUser:
    """
    Attributes:
        data (GetApiPlaylistsResponse200DataItemRelationshipsUserData):
    """

    data: GetApiPlaylistsResponse200DataItemRelationshipsUserData
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = self.data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_api_playlists_response_200_data_item_relationships_user_data import (
            GetApiPlaylistsResponse200DataItemRelationshipsUserData,
        )

        d = dict(src_dict)
        data = GetApiPlaylistsResponse200DataItemRelationshipsUserData.from_dict(d.pop("data"))

        get_api_playlists_response_200_data_item_relationships_user = cls(
            data=data,
        )

        get_api_playlists_response_200_data_item_relationships_user.additional_properties = d
        return get_api_playlists_response_200_data_item_relationships_user

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
