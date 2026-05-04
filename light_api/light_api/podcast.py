"""Podcast management for Light devices."""

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from open_api_specification_client.api.default import (
    delete_api_followed_podcasts_followed_podcast_id,
    get_api_followed_podcasts,
    post_api_followed_podcasts,
    post_api_podcasts,
)
from open_api_specification_client.models import (
    PostApiFollowedPodcastsBody,
    PostApiFollowedPodcastsBodyData,
    PostApiFollowedPodcastsBodyDataRelationships,
    PostApiFollowedPodcastsBodyDataType,
    PostApiPodcastsBody,
    PostApiPodcastsBodyData,
    PostApiPodcastsBodyDataAttributes,
    PostApiPodcastsBodyDataType,
)
from open_api_specification_client.models.post_api_followed_podcasts_body_data_relationships_device_tool import (
    PostApiFollowedPodcastsBodyDataRelationshipsDeviceTool,
)
from open_api_specification_client.models.post_api_followed_podcasts_body_data_relationships_device_tool_data import (
    PostApiFollowedPodcastsBodyDataRelationshipsDeviceToolData,
)
from open_api_specification_client.models.post_api_followed_podcasts_body_data_relationships_device_tool_data_type import (
    PostApiFollowedPodcastsBodyDataRelationshipsDeviceToolDataType,
)
from open_api_specification_client.models.post_api_followed_podcasts_body_data_relationships_podcast import (
    PostApiFollowedPodcastsBodyDataRelationshipsPodcast,
)
from open_api_specification_client.models.post_api_followed_podcasts_body_data_relationships_podcast_data import (
    PostApiFollowedPodcastsBodyDataRelationshipsPodcastData,
)
from open_api_specification_client.models.post_api_followed_podcasts_body_data_relationships_podcast_data_type import (
    PostApiFollowedPodcastsBodyDataRelationshipsPodcastDataType,
)

if TYPE_CHECKING:
    from light_api.client import Light

log = logging.getLogger(f"light.{__name__}")


@dataclass
class LightPodcast:
    podcast_id: str
    followed_podcast_id: str
    title: str
    publisher: str
    rss_feed_url: str
    description: str | None


class LightPodcasts:
    def __init__(self, light: "Light") -> None:
        self._l = light

    def _ensure_device_tool_id(self) -> str:
        if self._l._podcast_device_tool_id is None:
            self._l._fetch_podcast_device_tool_id()
            self._l._save_cache()
        assert self._l._podcast_device_tool_id is not None
        return self._l._podcast_device_tool_id

    def get_podcasts(self) -> list[LightPodcast]:
        """Fetch all followed podcasts for this device."""
        device_tool_id = self._ensure_device_tool_id()

        resp = get_api_followed_podcasts.sync_detailed(
            client=self._l._api_client,
            device_tool_id=device_tool_id,
        )
        if resp.status_code != 200 or resp.parsed is None:
            raise RuntimeError(f"Get podcasts: {resp.status_code}")

        body = resp.parsed
        included_by_id = {
            item.id: item.attributes
            for item in body.included
            if item.type_ == "podcasts"
        }

        podcasts = []
        for item in body.data:
            podcast_id = item.attributes.podcast_id
            attrs = included_by_id.get(podcast_id)
            podcasts.append(
                LightPodcast(
                    podcast_id=podcast_id,
                    followed_podcast_id=item.id,
                    title=(attrs.title or "") if attrs and attrs.title else "",
                    publisher=(
                        (attrs.publisher or "") if attrs and attrs.publisher else ""
                    ),
                    rss_feed_url=(
                        (attrs.rss_feed_url or "")
                        if attrs and attrs.rss_feed_url
                        else ""
                    ),
                    description=(attrs.description or None) if attrs else None,
                )
            )
        return podcasts

    def delete_podcast_by_title(self, title: str) -> None:
        """Unfollow podcasts matching title (exact match)."""
        podcasts = self.get_podcasts()
        matches = [p for p in podcasts if p.title == title]
        if not matches:
            log.info(f"No podcast found with title: {title!r}")
            return
        for p in matches:
            resp = delete_api_followed_podcasts_followed_podcast_id.sync_detailed(
                followed_podcast_id=p.followed_podcast_id,
                client=self._l._api_client,
            )
            if not (200 <= resp.status_code < 300):
                raise RuntimeError(f"Delete podcast: {resp.status_code}")

    def add_podcast(self, rss_feed_url: str) -> LightPodcast:
        """Add a podcast to the device by RSS feed URL.

        Registers the podcast globally then follows it on the device.
        """
        device_tool_id = self._ensure_device_tool_id()

        create_resp = post_api_podcasts.sync_detailed(
            client=self._l._api_client,
            body=PostApiPodcastsBody(
                data=PostApiPodcastsBodyData(
                    type_=PostApiPodcastsBodyDataType.PODCASTS,
                    attributes=PostApiPodcastsBodyDataAttributes(
                        rss_feed_url=rss_feed_url,
                        title=None,
                        publisher=None,
                        description=None,
                        itunes_id=None,
                    ),
                )
            ),
        )
        if create_resp.status_code not in (200, 201) or create_resp.parsed is None:
            raise RuntimeError(f"Create podcast: {create_resp.status_code}")

        podcast_id = create_resp.parsed.data.id
        attrs = create_resp.parsed.data.attributes

        follow_resp = post_api_followed_podcasts.sync_detailed(
            client=self._l._api_client,
            body=PostApiFollowedPodcastsBody(
                data=PostApiFollowedPodcastsBodyData(
                    type_=PostApiFollowedPodcastsBodyDataType.FOLLOWED_PODCASTS,
                    relationships=PostApiFollowedPodcastsBodyDataRelationships(
                        device_tool=PostApiFollowedPodcastsBodyDataRelationshipsDeviceTool(
                            data=PostApiFollowedPodcastsBodyDataRelationshipsDeviceToolData(
                                type_=PostApiFollowedPodcastsBodyDataRelationshipsDeviceToolDataType.DEVICE_TOOLS,
                                id=device_tool_id,
                            )
                        ),
                        podcast=PostApiFollowedPodcastsBodyDataRelationshipsPodcast(
                            data=PostApiFollowedPodcastsBodyDataRelationshipsPodcastData(
                                type_=PostApiFollowedPodcastsBodyDataRelationshipsPodcastDataType.PODCASTS,
                                id=podcast_id,
                            )
                        ),
                    ),
                )
            ),
        )
        if follow_resp.status_code not in (200, 201) or follow_resp.parsed is None:
            raise RuntimeError(f"Follow podcast: {follow_resp.status_code}")

        followed_podcast_id = follow_resp.parsed.data.id

        return LightPodcast(
            podcast_id=podcast_id,
            followed_podcast_id=followed_podcast_id,
            title=attrs.title or "",
            publisher=attrs.publisher or "",
            rss_feed_url=attrs.rss_feed_url or rss_feed_url,
            description=attrs.description or None,
        )
