from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.post_api_followed_podcasts_response_201_data import PostApiFollowedPodcastsResponse201Data
    from ..models.post_api_followed_podcasts_response_201_included_item import (
        PostApiFollowedPodcastsResponse201IncludedItem,
    )
    from ..models.post_api_followed_podcasts_response_201_jsonapi import PostApiFollowedPodcastsResponse201Jsonapi


T = TypeVar("T", bound="PostApiFollowedPodcastsResponse201")


@_attrs_define
class PostApiFollowedPodcastsResponse201:
    """
    Attributes:
        data (PostApiFollowedPodcastsResponse201Data):
        included (list[PostApiFollowedPodcastsResponse201IncludedItem]):
        jsonapi (PostApiFollowedPodcastsResponse201Jsonapi):
    """

    data: PostApiFollowedPodcastsResponse201Data
    included: list[PostApiFollowedPodcastsResponse201IncludedItem]
    jsonapi: PostApiFollowedPodcastsResponse201Jsonapi
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = self.data.to_dict()

        included = []
        for included_item_data in self.included:
            included_item = included_item_data.to_dict()
            included.append(included_item)

        jsonapi = self.jsonapi.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "included": included,
                "jsonapi": jsonapi,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_api_followed_podcasts_response_201_data import PostApiFollowedPodcastsResponse201Data
        from ..models.post_api_followed_podcasts_response_201_included_item import (
            PostApiFollowedPodcastsResponse201IncludedItem,
        )
        from ..models.post_api_followed_podcasts_response_201_jsonapi import PostApiFollowedPodcastsResponse201Jsonapi

        d = dict(src_dict)
        data = PostApiFollowedPodcastsResponse201Data.from_dict(d.pop("data"))

        included = []
        _included = d.pop("included")
        for included_item_data in _included:
            included_item = PostApiFollowedPodcastsResponse201IncludedItem.from_dict(included_item_data)

            included.append(included_item)

        jsonapi = PostApiFollowedPodcastsResponse201Jsonapi.from_dict(d.pop("jsonapi"))

        post_api_followed_podcasts_response_201 = cls(
            data=data,
            included=included,
            jsonapi=jsonapi,
        )

        post_api_followed_podcasts_response_201.additional_properties = d
        return post_api_followed_podcasts_response_201

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
