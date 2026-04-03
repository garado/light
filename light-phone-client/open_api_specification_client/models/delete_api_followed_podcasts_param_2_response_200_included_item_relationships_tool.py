from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.delete_api_followed_podcasts_param_2_response_200_included_item_relationships_tool_data import (
        DeleteApiFollowedPodcastsParam2Response200IncludedItemRelationshipsToolData,
    )


T = TypeVar("T", bound="DeleteApiFollowedPodcastsParam2Response200IncludedItemRelationshipsTool")


@_attrs_define
class DeleteApiFollowedPodcastsParam2Response200IncludedItemRelationshipsTool:
    """
    Attributes:
        data (DeleteApiFollowedPodcastsParam2Response200IncludedItemRelationshipsToolData):
    """

    data: DeleteApiFollowedPodcastsParam2Response200IncludedItemRelationshipsToolData
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
        from ..models.delete_api_followed_podcasts_param_2_response_200_included_item_relationships_tool_data import (
            DeleteApiFollowedPodcastsParam2Response200IncludedItemRelationshipsToolData,
        )

        d = dict(src_dict)
        data = DeleteApiFollowedPodcastsParam2Response200IncludedItemRelationshipsToolData.from_dict(d.pop("data"))

        delete_api_followed_podcasts_param_2_response_200_included_item_relationships_tool = cls(
            data=data,
        )

        delete_api_followed_podcasts_param_2_response_200_included_item_relationships_tool.additional_properties = d
        return delete_api_followed_podcasts_param_2_response_200_included_item_relationships_tool

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
