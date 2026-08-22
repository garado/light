"""Podcast management for Light devices."""

import dataclasses
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from light_api import cache

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


@dataclass
class PodcastAddResult:
    rss_feed_url: str
    success: bool
    podcast: LightPodcast | None
    error: str | None


class LightPodcasts:
    def __init__(self, light: "Light") -> None:
        self._l = light

    def get_podcasts(self) -> list[LightPodcast]:
        """Fetch all followed podcasts for this device."""
        if self._l._cache_enabled:
            cached = cache.load(cache.CacheModule.PODCASTS, self._l._api_token)
            if cached is not None:
                return [LightPodcast(**d) for d in cached]

        resp = get_api_followed_podcasts.sync_detailed(
            client=self._l._api_client,
            device_tool_id=self._l._device_tool_ids["podcast"],
        )
        body = self._l._ensure_ok(resp, "Get podcasts", require_parsed=True)
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

        if self._l._cache_enabled:
            cache.save(
                cache.CacheModule.PODCASTS,
                self._l._api_token,
                [dataclasses.asdict(p) for p in podcasts],
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
            self.delete_podcast_by_id(p.followed_podcast_id)

    def delete_podcast_by_id(self, followed_podcast_id: str) -> None:
        """Unfollow a podcast by its followed_podcast_id (see `get_podcasts`)."""
        resp = delete_api_followed_podcasts_followed_podcast_id.sync_detailed(
            followed_podcast_id=followed_podcast_id,
            client=self._l._api_client,
        )
        self._l._ensure_ok(resp, "Delete podcast", ok_codes=range(200, 300))

        if self._l._cache_enabled:
            cache.invalidate(cache.CacheModule.PODCASTS)

    def add_podcast(self, rss_feed_url: str) -> LightPodcast:
        """Add a podcast to the device by RSS feed URL.

        Registers the podcast globally then follows it on the device.
        """
        device_tool_id = self._l._device_tool_ids["podcast"]

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
        created = self._l._ensure_ok(
            create_resp, "Create podcast", ok_codes=(200, 201), require_parsed=True
        )

        podcast_id = created.data.id
        attrs = created.data.attributes

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
        followed = self._l._ensure_ok(
            follow_resp, "Follow podcast", ok_codes=(200, 201), require_parsed=True
        )

        followed_podcast_id = followed.data.id

        if self._l._cache_enabled:
            cache.invalidate(cache.CacheModule.PODCASTS)

        return LightPodcast(
            podcast_id=podcast_id,
            followed_podcast_id=followed_podcast_id,
            title=attrs.title or "",
            publisher=attrs.publisher or "",
            rss_feed_url=attrs.rss_feed_url or rss_feed_url,
            description=attrs.description or None,
        )
