from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_api_playlists_response_200_included_item_relationships_device import (
        GetApiPlaylistsResponse200IncludedItemRelationshipsDevice,
    )
    from ..models.get_api_playlists_response_200_included_item_relationships_tool import (
        GetApiPlaylistsResponse200IncludedItemRelationshipsTool,
    )


T = TypeVar("T", bound="GetApiPlaylistsResponse200IncludedItemRelationships")


@_attrs_define
class GetApiPlaylistsResponse200IncludedItemRelationships:
    """
    Attributes:
        device (GetApiPlaylistsResponse200IncludedItemRelationshipsDevice):
        tool (GetApiPlaylistsResponse200IncludedItemRelationshipsTool):
    """

    device: GetApiPlaylistsResponse200IncludedItemRelationshipsDevice
    tool: GetApiPlaylistsResponse200IncludedItemRelationshipsTool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device = self.device.to_dict()

        tool = self.tool.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "device": device,
                "tool": tool,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_api_playlists_response_200_included_item_relationships_device import (
            GetApiPlaylistsResponse200IncludedItemRelationshipsDevice,
        )
        from ..models.get_api_playlists_response_200_included_item_relationships_tool import (
            GetApiPlaylistsResponse200IncludedItemRelationshipsTool,
        )

        d = dict(src_dict)
        device = GetApiPlaylistsResponse200IncludedItemRelationshipsDevice.from_dict(d.pop("device"))

        tool = GetApiPlaylistsResponse200IncludedItemRelationshipsTool.from_dict(d.pop("tool"))

        get_api_playlists_response_200_included_item_relationships = cls(
            device=device,
            tool=tool,
        )

        get_api_playlists_response_200_included_item_relationships.additional_properties = d
        return get_api_playlists_response_200_included_item_relationships

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
