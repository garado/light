from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_api_followed_podcasts_response_201_included_item_attributes_config import (
        PostApiFollowedPodcastsResponse201IncludedItemAttributesConfig,
    )


T = TypeVar("T", bound="PostApiFollowedPodcastsResponse201IncludedItemAttributes")


@_attrs_define
class PostApiFollowedPodcastsResponse201IncludedItemAttributes:
    """
    Attributes:
        description (None | str | Unset):
        itunes_id (None | str | Unset):
        publisher (str | Unset):
        rss_feed_url (str | Unset):
        title (str | Unset):
        config (PostApiFollowedPodcastsResponse201IncludedItemAttributesConfig | Unset):
        deleted_at (None | Unset):
    """

    description: None | str | Unset = UNSET
    itunes_id: None | str | Unset = UNSET
    publisher: str | Unset = UNSET
    rss_feed_url: str | Unset = UNSET
    title: str | Unset = UNSET
    config: PostApiFollowedPodcastsResponse201IncludedItemAttributesConfig | Unset = UNSET
    deleted_at: None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        itunes_id: None | str | Unset
        if isinstance(self.itunes_id, Unset):
            itunes_id = UNSET
        else:
            itunes_id = self.itunes_id

        publisher = self.publisher

        rss_feed_url = self.rss_feed_url

        title = self.title

        config: dict[str, Any] | Unset = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        deleted_at = self.deleted_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if description is not UNSET:
            field_dict["description"] = description
        if itunes_id is not UNSET:
            field_dict["itunes_id"] = itunes_id
        if publisher is not UNSET:
            field_dict["publisher"] = publisher
        if rss_feed_url is not UNSET:
            field_dict["rss_feed_url"] = rss_feed_url
        if title is not UNSET:
            field_dict["title"] = title
        if config is not UNSET:
            field_dict["config"] = config
        if deleted_at is not UNSET:
            field_dict["deleted_at"] = deleted_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_api_followed_podcasts_response_201_included_item_attributes_config import (
            PostApiFollowedPodcastsResponse201IncludedItemAttributesConfig,
        )

        d = dict(src_dict)

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_itunes_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        itunes_id = _parse_itunes_id(d.pop("itunes_id", UNSET))

        publisher = d.pop("publisher", UNSET)

        rss_feed_url = d.pop("rss_feed_url", UNSET)

        title = d.pop("title", UNSET)

        _config = d.pop("config", UNSET)
        config: PostApiFollowedPodcastsResponse201IncludedItemAttributesConfig | Unset
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = PostApiFollowedPodcastsResponse201IncludedItemAttributesConfig.from_dict(_config)

        deleted_at = d.pop("deleted_at", UNSET)

        post_api_followed_podcasts_response_201_included_item_attributes = cls(
            description=description,
            itunes_id=itunes_id,
            publisher=publisher,
            rss_feed_url=rss_feed_url,
            title=title,
            config=config,
            deleted_at=deleted_at,
        )

        post_api_followed_podcasts_response_201_included_item_attributes.additional_properties = d
        return post_api_followed_podcasts_response_201_included_item_attributes

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
