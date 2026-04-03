from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PostApiPodcastsResponse201DataAttributes")


@_attrs_define
class PostApiPodcastsResponse201DataAttributes:
    """
    Attributes:
        description (str):
        itunes_id (None):
        publisher (str):
        rss_feed_url (str):
        title (str):
    """

    description: str
    itunes_id: None
    publisher: str
    rss_feed_url: str
    title: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        description = self.description

        itunes_id = self.itunes_id

        publisher = self.publisher

        rss_feed_url = self.rss_feed_url

        title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "description": description,
                "itunes_id": itunes_id,
                "publisher": publisher,
                "rss_feed_url": rss_feed_url,
                "title": title,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        description = d.pop("description")

        itunes_id = d.pop("itunes_id")

        publisher = d.pop("publisher")

        rss_feed_url = d.pop("rss_feed_url")

        title = d.pop("title")

        post_api_podcasts_response_201_data_attributes = cls(
            description=description,
            itunes_id=itunes_id,
            publisher=publisher,
            rss_feed_url=rss_feed_url,
            title=title,
        )

        post_api_podcasts_response_201_data_attributes.additional_properties = d
        return post_api_podcasts_response_201_data_attributes

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
