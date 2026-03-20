"""Podcast management for Light devices."""

from dataclasses import dataclass
from typing import TYPE_CHECKING
from rich.console import Console

import endpoints

if TYPE_CHECKING:
    from core import Light

console = Console()


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
        resp = self._l._request(
            f"{endpoints.FOLLOWED_PODCASTS}?device_tool_id={device_tool_id}",
        )
        self._l._check_response(resp, "get podcasts")
        body: dict[str, Any] = resp.json()

        included_by_id: dict[str, dict[str, Any]] = {
            item["id"]: item["attributes"]
            for item in body.get("included", [])
            if item["type"] == "podcasts"
        }

        podcasts = []
        for item in body["data"]:
            podcast_id: str = item["attributes"]["podcast_id"]
            attrs = included_by_id.get(podcast_id, {})
            podcasts.append(
                LightPodcast(
                    podcast_id=podcast_id,
                    followed_podcast_id=item["id"],
                    title=attrs.get("title") or "",
                    publisher=attrs.get("publisher") or "",
                    rss_feed_url=attrs.get("rss_feed_url") or "",
                    description=attrs.get("description"),
                )
            )
        return podcasts

    def delete_podcast_by_title(self, title: str) -> None:
        """Unfollow podcasts matching title (exact match)."""
        podcasts = self.get_podcasts()
        matches = [p for p in podcasts if p.title == title]
        if not matches:
            console.print(f"[yellow]No podcast found with title: {title}[/yellow]")
            return
        for p in matches:
            resp = self._l._request(
                endpoints.followed_podcast(p.followed_podcast_id),
                method="DELETE",
            )
            self._l._check_response(resp, "delete podcast")

    def add_podcast(self, rss_feed_url: str) -> LightPodcast:
        """Add a podcast to the device by RSS feed URL.

        Registers the podcast globally then follows it on the device.
        """
        device_tool_id = self._ensure_device_tool_id()

        resp = self._l._request(
            endpoints.PODCASTS,
            method="POST",
            data={
                "data": {
                    "attributes": {
                        "description": None,
                        "itunes_id": None,
                        "publisher": None,
                        "rss_feed_url": rss_feed_url,
                        "title": None,
                    },
                    "type": "podcasts",
                }
            },
        )
        self._l._check_response(resp, "create podcast")
        body: dict[str, Any] = resp.json()
        podcast_id: str = body["data"]["id"]
        attrs: dict[str, Any] = body["data"]["attributes"]

        resp = self._l._request(
            endpoints.FOLLOWED_PODCASTS,
            method="POST",
            data={
                "data": {
                    "relationships": {
                        "device_tool": {
                            "data": {"type": "device_tools", "id": device_tool_id}
                        },
                        "podcast": {"data": {"type": "podcasts", "id": podcast_id}},
                    },
                    "type": "followed_podcasts",
                }
            },
        )
        self._l._check_response(resp, "follow podcast")
        followed_podcast_id: str = resp.json()["data"]["id"]

        return LightPodcast(
            podcast_id=podcast_id,
            followed_podcast_id=followed_podcast_id,
            title=attrs.get("title") or "",
            publisher=attrs.get("publisher") or "",
            rss_feed_url=attrs.get("rss_feed_url") or rss_feed_url,
            description=attrs.get("description"),
        )
