"""Music management for Light devices."""

from enum import StrEnum
import logging
import os
import re
from typing import Any, Callable, Literal

from dataclasses import dataclass
from mutagen import File
from rich.console import Console

from light_api.client import Light
from open_api_specification_client.api.default import (
    delete_api_audios_param2,
    get_api_playlist_items,
    get_api_playlists,
    patch_api_audios_param2,
    patch_api_playlist_items_param2,
    post_api_audios,
    post_api_playlists_sort_mode,
)
from open_api_specification_client.models import (
    PatchApiAudiosParam2Body,
    PatchApiAudiosParam2BodyData,
    PatchApiAudiosParam2BodyDataAttributes,
    PatchApiAudiosParam2BodyDataType,
    PatchApiPlaylistItemsParam2Body,
    PatchApiPlaylistItemsParam2BodyData,
    PatchApiPlaylistItemsParam2BodyDataAttributes,
    PatchApiPlaylistItemsParam2BodyDataType,
    PostApiAudiosBody,
    PostApiAudiosBodyData,
    PostApiAudiosBodyDataAttributes,
    PostApiAudiosBodyDataType,
    PostApiPlaylistsSortModeBody,
    PostApiPlaylistsSortModeBodySortMode,
)

console = Console()
log = logging.getLogger(f"light.{__name__}")


@dataclass
class LightTrack:
    playlist_item_id: str
    audio_id: str
    presigned_url: str
    title: str
    artist: str
    album: str  # unused, but Light makes it available


class SortMode(StrEnum):
    # native API sort modes
    RANK = "rank"
    ARTIST_ASC = "artists_asc"
    ARTIST_DESC = "artists_desc"

    # implemented locally via position patching
    TITLE_ASC = "title_asc"
    TITLE_DESC = "title_desc"


class LightMusic:
    def __init__(self, light: Light) -> None:
        self._l: Light = light

        self._tracks: list[LightTrack]  # lazily initialized

    def _init_tracks(self):
        if not hasattr(self, "_tracks"):
            self._tracks = self.get_tracks()

    def get_sort_mode(self) -> SortMode:
        """Get the current sort mode.

        Returns:
            The currently-applied sort mode: artists_asc, artists_desc, or rank (unsorted).

        Note:
            Title-based sort modes (title_asc, title_desc) are custom, local-only modes and
            cannot be detected from the API.
        """
        resp = get_api_playlists.sync_detailed(
            client=self._l._api_client,
            device_tool_id=self._l._device_tool_id,
        )
        if resp.status_code != 200 or resp.parsed is None:
            raise RuntimeError(f"get sort mode: {resp.status_code}")

        playlist = resp.parsed.data[0]
        return SortMode(playlist.attributes.sort_mode)

    def set_sort_mode(self, sort_mode: SortMode):
        """Set sort mode.

        Args:
            sort_mode: The new sort mode to set.
        """
        if sort_mode in (SortMode.ARTIST_ASC, SortMode.ARTIST_DESC, SortMode.RANK):
            if sort_mode is not SortMode.RANK:
                # these two seem to be inverted?
                # have i reverse engineered a bug in the light api endpoints?!
                sort_mode = (
                    SortMode.ARTIST_DESC
                    if sort_mode == SortMode.ARTIST_ASC
                    else SortMode.ARTIST_ASC
                )

            resp = post_api_playlists_sort_mode.sync_detailed(
                client=self._l._api_client,
                body=PostApiPlaylistsSortModeBody(
                    playlist_id=self._l._playlist_id,
                    device_tool_id=self._l._device_tool_id,
                    sort_mode=PostApiPlaylistsSortModeBodySortMode(sort_mode),
                ),
            )
            if not (200 <= resp.status_code < 300):
                raise RuntimeError(f"set sort mode: {resp.status_code}")

            console.print("[green]Sort mode set successfully.[/green]")

        else:
            self._sort_by_title(sort_mode == SortMode.TITLE_DESC)

    def get_tracks(self) -> list[LightTrack]:
        """Fetch list of all tracks on the device.

        Returns:
            List of LightTracks in the current playlist order.
        """
        resp = get_api_playlist_items.sync_detailed(
            client=self._l._api_client,
            playlist_ids=self._l._playlist_id,
            device_tool_id=self._l._device_tool_id,
        )
        if resp.status_code != 200 or resp.parsed is None:
            raise RuntimeError(f"get tracks: {resp.status_code}")

        body = resp.parsed

        file_attrs = {
            item.id: item.attributes for item in body.included if item.type_ == "files"
        }
        audio_info = {
            item.id: {
                "attrs": item.attributes,
                "file_id": item.relationships.processed_file.data.id,
            }
            for item in body.included
            if item.type_ == "audios"
        }

        items = sorted(body.data, key=lambda x: x.attributes.position)

        return [
            LightTrack(
                playlist_item_id=item.id,
                audio_id=(audio_id := item.relationships.audio.data.id),
                presigned_url=file_attrs[audio_info[audio_id]["file_id"]].presigned_url
                or "",
                title=audio_info[audio_id]["attrs"].title or "",
                artist=audio_info[audio_id]["attrs"].artist or "",
                album=audio_info[audio_id]["attrs"].album or "",
            )
            for item in items
        ]

    def delete_tracks_predicate(
        self, predicate: Callable[[LightTrack], bool]
    ) -> None:
        """Delete tracks from device, using a predicate to match targets for deletion.

        Args:
            predicate: Predicate for deletion target matching.
        """
        self._init_tracks()

        to_delete = [t for t in self._tracks if predicate(t)]

        if not to_delete:
            log.info("no matching tracks")
            return

        tracks_deleted = 0
        for track in to_delete:
            resp = delete_api_audios_param2.sync_detailed(
                param2=track.audio_id,
                client=self._l._api_client,
            )

            if not (200 <= resp.status_code < 300):
                console.print(
                    f"[red]Failed to delete: {track.title} (status {resp.status_code})[/red]"
                )
            else:
                console.print(f"[green]Deleted: {track.title}[/green]")
                tracks_deleted += 1

        console.print(
            f"[green]Deleted {tracks_deleted}/{len(to_delete)} tracks [/green]"
        )

    def delete_tracks_by_title(self, titles: list[str]) -> None:
        """Delete tracks by title.

        Args:
            titles: List of track titles as they appear in the Light dashboard.
        """
        self.delete_tracks_predicate(lambda t: t.title in set(titles))

    def delete_tracks_by_artist(self, artists: list[str]) -> None:
        """Delete tracks by artist.

        Args:
            artists: List of artists as they appear in the Light dashboard.
        """
        self.delete_tracks_predicate(lambda t: t.artist in set(artists))

    def delete_tracks_by_title_regex(self, pattern: str) -> None:
        """Delete tracks whose title matches a regex pattern.

        Args:
            pattern: Regex pattern matched against each track's title.
                     Example: r"^The" to match all tracks starting with "The".
        """
        self.delete_tracks_predicate(lambda t: bool(re.match(pattern, t.title)))

    def delete_tracks_by_artist_regex(self, pattern: str) -> None:
        """Delete tracks whose artist matches a regex pattern.

        Args:
            pattern: Regex pattern matched against each track's artist name.
                     Example: r"^The" to match all artists starting with "The".
        """
        self.delete_tracks_predicate(lambda t: bool(re.match(pattern, t.artist)))

    def upload_tracks(
        self,
        files: list[str],
        allow_duplicates: bool = False,
        match_title_by: Literal["metadata", "filename"] = "metadata",
    ) -> None:
        """Upload tracks to device.

        Args:
            files: List of paths to audio files to upload.
            allow_duplicates: If False (default), existing tracks with matching titles are
                              deleted before uploading. If True, duplicates are kept.
            match_title_by: How to determine a track's title for duplicate detection.
                            "metadata" (default) reads the title from the file's ID3/audio tags.
                            "filename" uses the filename (without extension) as the title.
        """
        if not allow_duplicates:
            titles: list[str]

            if match_title_by == "metadata":
                titles = []
                for s in files:
                    f = File(s, easy=True)
                    if f is None:
                        raise ValueError(f"Could not read metadata from {s}")
                    titles.append(f.get("title", ["Unknown Title"])[0])
            else:
                titles = [os.path.splitext(os.path.basename(s))[0] for s in files]

            self.delete_tracks_by_title(titles)

        for file_path in files:
            console.print(f"[green]Uploading {file_path}[/green]")

            if not os.path.exists(file_path):
                console.print(
                    f"[yellow]Warning: file not found, skipping: {file_path}[/yellow]"
                )
                continue

            create_resp = post_api_audios.sync_detailed(
                client=self._l._api_client,
                body=PostApiAudiosBody(
                    data=PostApiAudiosBodyData(
                        type_=PostApiAudiosBodyDataType.AUDIOS,
                        attributes=PostApiAudiosBodyDataAttributes(
                            filename=os.path.basename(file_path),
                            device_tool_id=self._l._device_tool_id,
                        ),
                    )
                ),
            )
            if create_resp.status_code not in (200, 201) or create_resp.parsed is None:
                raise RuntimeError(
                    f"create audio record for {os.path.basename(file_path)}: {create_resp.status_code}"
                )

            presigned_url = next(
                item.attributes.presigned_url
                for item in create_resp.parsed.included
                if item.type_ == "files"
            )

            with open(file_path, "rb") as f:
                data = f.read()

            put_resp = self._l._fetch(
                presigned_url,
                method="PUT",
                headers={"Content-Type": "audio/mpeg"},
                data=data,
                timeout=300_000,
            )

            self._l._check_response(put_resp, f"upload {os.path.basename(file_path)}")

        console.print(f"[green]All uploads complete.[/green]")
        console.print(
            f"[green]It may take some time to process and appear on your device.[/green]"
        )

    def update_track_metadata(
        self, audio_id: str, title: str | None = None, artist: str | None = None
    ):
        """Update metadata (title, artist) for a track.

        Args:
            audio_id: The audio_id for the track to edit.
            title: The new title, or None for no changes.
            artist: The new artist, or None for no changes.
        """
        from open_api_specification_client.types import UNSET

        resp = patch_api_audios_param2.sync_detailed(
            param2=audio_id,
            client=self._l._api_client,
            body=PatchApiAudiosParam2Body(
                data=PatchApiAudiosParam2BodyData(
                    id=audio_id,
                    type_=PatchApiAudiosParam2BodyDataType.PLAYLIST_ITEMS,
                    attributes=PatchApiAudiosParam2BodyDataAttributes(
                        title=title if title is not None else UNSET,
                        artist=artist if artist is not None else UNSET,
                    ),
                )
            ),
        )
        if not (200 <= resp.status_code < 300):
            raise RuntimeError(f"update metadata: {resp.status_code}")

        console.print(f"[green]Update metadata successfully.[/green]")

    def _sort_by_title(self, descending: bool = False) -> None:
        """Sort tracks on device by title.

        The dashboard has no native sort-by-title, so we PATCH the position of
        each track directly.

        Args:
            descending: True to sort descending; False for ascending.

        Note:
            @light - i am begging you... please allow sorting by title. crying emoji
        """
        tracks: list[LightTrack] = self.get_tracks()
        sorted_tracks: list[LightTrack] = sorted(
            tracks, key=lambda t: t.title.casefold(), reverse=descending
        )

        # our custom sort is a subset of rank
        self.set_sort_mode(SortMode.RANK)

        original_positions: dict[str, int] = {
            t.audio_id: i for i, t in enumerate(tracks)
        }

        for new_position, track in enumerate(sorted_tracks):
            if original_positions[track.audio_id] == new_position:
                continue

            resp = patch_api_playlist_items_param2.sync_detailed(
                param2=track.playlist_item_id,
                client=self._l._api_client,
                body=PatchApiPlaylistItemsParam2Body(
                    data=PatchApiPlaylistItemsParam2BodyData(
                        id=track.playlist_item_id,
                        type_=PatchApiPlaylistItemsParam2BodyDataType.PLAYLIST_ITEMS,
                        attributes=PatchApiPlaylistItemsParam2BodyDataAttributes(
                            position=new_position,
                        ),
                    )
                ),
            )
            if not (200 <= resp.status_code < 300):
                raise RuntimeError(
                    f"sort by title position {new_position}: {resp.status_code}"
                )
