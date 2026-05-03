from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostApiPodcastsBodyDataAttributes")


@_attrs_define
class PostApiPodcastsBodyDataAttributes:
    """
    Attributes:
        rss_feed_url (str):
        title (None | str | Unset):
        publisher (None | str | Unset):
        description (None | str | Unset):
        itunes_id (None | str | Unset):
    """

    rss_feed_url: str
    title: None | str | Unset = UNSET
    publisher: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    itunes_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        rss_feed_url = self.rss_feed_url

        title: None | str | Unset
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        publisher: None | str | Unset
        if isinstance(self.publisher, Unset):
            publisher = UNSET
        else:
            publisher = self.publisher

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

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "rss_feed_url": rss_feed_url,
            }
        )
        if title is not UNSET:
            field_dict["title"] = title
        if publisher is not UNSET:
            field_dict["publisher"] = publisher
        if description is not UNSET:
            field_dict["description"] = description
        if itunes_id is not UNSET:
            field_dict["itunes_id"] = itunes_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        rss_feed_url = d.pop("rss_feed_url")

        def _parse_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        title = _parse_title(d.pop("title", UNSET))

        def _parse_publisher(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        publisher = _parse_publisher(d.pop("publisher", UNSET))

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

        post_api_podcasts_body_data_attributes = cls(
            rss_feed_url=rss_feed_url,
            title=title,
            publisher=publisher,
            description=description,
            itunes_id=itunes_id,
        )

        post_api_podcasts_body_data_attributes.additional_properties = d
        return post_api_podcasts_body_data_attributes

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
