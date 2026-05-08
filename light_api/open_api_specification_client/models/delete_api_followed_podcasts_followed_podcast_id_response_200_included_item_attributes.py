from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.delete_api_followed_podcasts_followed_podcast_id_response_200_included_item_attributes_config import (
        DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemAttributesConfig,
    )


T = TypeVar("T", bound="DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemAttributes")


@_attrs_define
class DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemAttributes:
    """
    Attributes:
        description (None | Unset):
        itunes_id (str | Unset):
        publisher (str | Unset):
        rss_feed_url (str | Unset):
        title (str | Unset):
        config (DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemAttributesConfig | Unset):
        deleted_at (None | Unset):
    """

    description: None | Unset = UNSET
    itunes_id: str | Unset = UNSET
    publisher: str | Unset = UNSET
    rss_feed_url: str | Unset = UNSET
    title: str | Unset = UNSET
    config: DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemAttributesConfig | Unset = UNSET
    deleted_at: None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        description = self.description

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
        from ..models.delete_api_followed_podcasts_followed_podcast_id_response_200_included_item_attributes_config import (
            DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemAttributesConfig,
        )

        d = dict(src_dict)
        description = d.pop("description", UNSET)

        itunes_id = d.pop("itunes_id", UNSET)

        publisher = d.pop("publisher", UNSET)

        rss_feed_url = d.pop("rss_feed_url", UNSET)

        title = d.pop("title", UNSET)

        _config = d.pop("config", UNSET)
        config: DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemAttributesConfig | Unset
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = DeleteApiFollowedPodcastsFollowedPodcastIdResponse200IncludedItemAttributesConfig.from_dict(
                _config
            )

        deleted_at = d.pop("deleted_at", UNSET)

        delete_api_followed_podcasts_followed_podcast_id_response_200_included_item_attributes = cls(
            description=description,
            itunes_id=itunes_id,
            publisher=publisher,
            rss_feed_url=rss_feed_url,
            title=title,
            config=config,
            deleted_at=deleted_at,
        )

        delete_api_followed_podcasts_followed_podcast_id_response_200_included_item_attributes.additional_properties = d
        return delete_api_followed_podcasts_followed_podcast_id_response_200_included_item_attributes

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
