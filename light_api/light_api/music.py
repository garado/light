"""Music management for Light devices."""

import httpx
import logging
import mimetypes
import os
import re
import tempfile
from enum import StrEnum
from typing import Callable

from dataclasses import dataclass
from mutagen._file import File

from light_api.client import Light
from open_api_specification_client.api.default import (
    delete_api_audios_audio_id,
    get_api_playlist_items,
    get_api_playlists,
    patch_api_audios_audio_id,
    patch_api_playlist_items_playlist_item_id,
    post_api_audios,
    post_api_playlists_sort_mode,
    post_api_audios_delete_all,
)
from open_api_specification_client.models import (
    PatchApiAudiosAudioIdBody,
    PatchApiAudiosAudioIdBodyData,
    PatchApiAudiosAudioIdBodyDataAttributes,
    PatchApiAudiosAudioIdBodyDataType,
    PatchApiPlaylistItemsPlaylistItemIdBody,
    PatchApiPlaylistItemsPlaylistItemIdBodyData,
    PatchApiPlaylistItemsPlaylistItemIdBodyDataAttributes,
    PatchApiPlaylistItemsPlaylistItemIdBodyDataType,
    PostApiAudiosBody,
    PostApiAudiosBodyData,
    PostApiAudiosBodyDataAttributes,
    PostApiAudiosBodyDataType,
    PostApiAudiosDeleteAllBody,
    PostApiPlaylistsSortModeBody,
    PostApiPlaylistsSortModeBodySortMode,
)

log = logging.getLogger(f"light.{__name__}")


@dataclass
class LightTrack:
    playlist_item_id: str
    audio_id: str
    title: str
    artist: str
    album: str  # unused by dashboard, but they make it available


class SortMode(StrEnum):
    # native API sort modes
    RANK = "rank"
    ARTIST_ASC = "artists_asc"
    ARTIST_DESC = "artists_desc"

    # implemented locally via position patching
    TITLE_ASC = "title_asc"
    TITLE_DESC = "title_desc"
    ARTIST_ALBUM_ASC = "aa_asc"
    ARTIST_ALBUM_DESC = "aa_desc"


def _flac_to_mp3(flac_path: str) -> str:
    """Convert a FLAC file to MP3 in a tempfile, preserving metadata. Returns the temp path."""
    import subprocess
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp.close()
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", flac_path, "-map_metadata", "0", "-ab", "320k", tmp.name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        os.unlink(tmp.name)
        raise RuntimeError(f"ffmpeg conversion failed for {flac_path}")
    return tmp.name


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
            The currently-applied stock sort mode: artists_asc, artists_desc, or rank (unsorted).

        Note:
            Doesn't report custom sort modes like artist-album or title.
        """
        resp = self._l.call_api(
            get_api_playlists.sync_detailed,
            client=self._l._api_client,
            device_tool_id=self._l._device_tool_ids["music"],
        )
        parsed = self._l._ensure_ok(resp, "Get sort mode", require_parsed=True)

        playlist = parsed.data[0]
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

            resp = self._l.call_api(
                post_api_playlists_sort_mode.sync_detailed,
                client=self._l._api_client,
                body=PostApiPlaylistsSortModeBody(
                    playlist_id=self._l._playlist_id,
                    device_tool_id=self._l._device_tool_ids["music"],
                    sort_mode=PostApiPlaylistsSortModeBodySortMode(sort_mode),
                ),
            )

            self._l._ensure_ok(resp, "Set sort mode", ok_codes=range(200, 300))

            log.info(f"Sort mode set")
        elif sort_mode in (SortMode.TITLE_ASC, SortMode.TITLE_DESC):
            self._sort_by_title(sort_mode == SortMode.TITLE_DESC)
        elif sort_mode in (SortMode.ARTIST_ALBUM_ASC, SortMode.ARTIST_ALBUM_DESC):
            self._sort_by_artist_album(sort_mode == SortMode.ARTIST_ALBUM_DESC)

    def get_tracks(self) -> list[LightTrack]:
        """Fetch list of all tracks on the device.

        Returns:
            List of LightTracks in the current playlist order.
        """
        resp = self._l.call_api(
            get_api_playlist_items.sync_detailed,
            client=self._l._api_client,
            playlist_ids=self._l._playlist_id,
            device_tool_id=self._l._device_tool_ids["music"],
        )
        body = self._l._ensure_ok(resp, "Get tracks", require_parsed=True)

        if not body.data:
            return []

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
                title=audio_info[audio_id]["attrs"].title or "",
                artist=audio_info[audio_id]["attrs"].artist or "",
                album=audio_info[audio_id]["attrs"].album or "",
            )
            for item in items
        ]

    def delete_all_tracks(self) -> None:
        """Delete all tracks from the device.

        Note: In API mode, there is NO confirmation before this happens. (In CLI/TUI there is.)
        If you're calling this method in API mode, I assume you know what you are doing.
        """
        resp = self._l.call_api(
            post_api_audios_delete_all.sync_detailed,
            client=self._l._api_client,
            body=PostApiAudiosDeleteAllBody(
                device_tool_id=self._l._device_tool_ids["music"]
            ),
        )
        self._l._ensure_ok(resp, "Failed to delete all tracks", ok_codes=range(200, 300))
        log.info("All tracks deleted")

    def delete_tracks_predicate(self, predicate: Callable[[LightTrack], bool]) -> None:
        """Delete tracks from device, using a predicate to match targets for deletion.

        Args:
            predicate: Predicate for deletion target matching.
        """
        self._init_tracks()

        to_delete = [t for t in self._tracks if predicate(t)]

        if not to_delete:
            log.info("No matching tracks")
            return

        tracks_deleted = 0
        for track in to_delete:
            resp = self._l.call_api(
                delete_api_audios_audio_id.sync_detailed,
                audio_id=track.audio_id,
                client=self._l._api_client,
            )

            if not (200 <= resp.status_code < 300):
                log.warning(f"Failed to delete {track.title!r}: {resp.status_code}")
            else:
                log.info(f"Deleted {track.title!r}")
                tracks_deleted += 1

        log.info(f"Deleted {tracks_deleted}/{len(to_delete)} tracks")

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

    def _track_identity(self, file_path: str) -> tuple[str, str]:
        """Return (title, artist) for an audio file at file_path.

        If the track has metadata for a field: use that metadata.
        If no metadata for a field: titles will fall back to just 'filename', and 
        artists will fall back to "Unknown", matching the dashboard's implementation.

        Args:
            file_path: File path of audio file to process.

        Returns:
            (title, artist) tuple representing that file's content.
        """
        tags = File(file_path, easy=True)
        title = (tags.get("title", [None])[0] if tags else None) or os.path.splitext(
            os.path.basename(file_path)
        )[0]
        artist = (tags.get("artist", [None])[0] if tags else None) or "Unknown"
        return title, artist

    def _find_matching_track(self, title: str, artist: str) -> LightTrack | None:
        """Find an existing track with an exact (title, artist) match."""
        for t in self._tracks:
            if t.title == title and t.artist == artist:
                return t
        return None

    def find_upload_matches(self, files: list[str]) -> dict[str, LightTrack]:
        """Given a list of local audio files, find those that already exist on the device and
        return the matching existing LightTrack instances.

        Args:
            files: A list of paths to audio files.

        Returns:
            A {file_path: LightTrack} dict.
        """
        self._init_tracks()
        matches: dict[str, LightTrack] = {}
        for file_path in files:
            title, artist = self._track_identity(file_path)
            match = self._find_matching_track(title, artist)
            if match is not None:
                matches[file_path] = match
        return matches

    def _resolve_upload_plan(
        self, files: list[str], allow_duplicates: bool, overwrite: bool
        ) -> tuple[list[str], list[LightTrack]]:
        """Return the subset of files to upload and the subset of files to overwrite after
        applying allow_duplicates/overwrite behavior flags.

        Returns:
            Tuple of lists. First item is list[str] of files to upload. Second item is list[LightTrack]
            of files to be overwritten.
        """
        if allow_duplicates:
            return (files, [])

        matches = self.find_upload_matches(files)
        to_delete = list({t.audio_id: t for t in matches.values()}.values()) if overwrite else []

        to_upload = []
        for file_path in files:
            match = matches.get(file_path)

            if match is None or overwrite:
                to_upload.append(file_path)
            else:
                log.info(f"Skipping {file_path!r}: matches existing ({match.title!r}, {match.artist!r})")

        return (to_upload, to_delete)

    def upload_tracks(
        self,
        files: list[str],
        allow_duplicates: bool = False,
        overwrite: bool = False,
        convert_flac: bool = True,
        on_progress: "Callable[[str, int, int], None] | None" = None,
    ) -> None:
        """Upload tracks to device.

        Args:
            files: List of paths to audio files to upload.
            allow_duplicates: If True, skip duplicate checking entirely and always upload,
                               potentially creating multiple tracks with the same title/artist.
            overwrite: If True, delete a file's matching existing track (if any) before
                       uploading it. If False (default), files matching an existing track
                       are skipped instead, leaving the existing track untouched.
        """
        if overwrite and allow_duplicates:
            raise ValueError("overwrite and allow_duplicates are mutually exclusive")

        manual_update_cmds = []

        existing_files: list[str] = []
        for file_path in files:
            if os.path.exists(file_path):
                existing_files.append(file_path)
            else:
                log.warning(f"File not found, skipping: {file_path}")

        to_upload, to_delete = self._resolve_upload_plan(
            existing_files, allow_duplicates, overwrite
        )

        if to_delete:
            audio_ids = {t.audio_id for t in to_delete}
            self.delete_tracks_predicate(lambda t: t.audio_id in audio_ids)

        for file_path in to_upload:
            log.info(f"Uploading {file_path}")

            tmp_path = None
            try:
                if convert_flac and file_path.lower().endswith(".flac"):
                    log.info(f"Converting {file_path} to MP3")
                    tmp_path = _flac_to_mp3(file_path)
                    upload_path = tmp_path
                else:
                    upload_path = file_path

                create_resp = self._l.call_api(
                    post_api_audios.sync_detailed,
                    client=self._l._api_client,
                    body=PostApiAudiosBody(
                        data=PostApiAudiosBodyData(
                            type_=PostApiAudiosBodyDataType.AUDIOS,
                            attributes=PostApiAudiosBodyDataAttributes(
                                filename=os.path.basename(upload_path),
                                device_tool_id=self._l._device_tool_ids["music"],
                            ),
                        )
                    ),
                )
                created = self._l._ensure_ok(
                    create_resp,
                    f"Create audio record for {os.path.basename(upload_path)}",
                    ok_codes=(200, 201),
                    require_parsed=True,
                )

                presigned_url = next(
                    item.attributes.presigned_url
                    for item in created.included
                    if item.type_ == "files"
                )

                content_type = mimetypes.guess_type(upload_path)[0] or "audio/mpeg"
                total = os.path.getsize(upload_path)
                filename = os.path.basename(upload_path)

                def _chunks(path: str, total: int, filename: str):
                    sent = 0
                    with open(path, "rb") as f:
                        while chunk := f.read(65536):
                            sent += len(chunk)
                            if on_progress:
                                on_progress(filename, sent, total)
                            yield chunk

                put_resp = httpx.put(
                    presigned_url,
                    content=_chunks(upload_path, total, filename),
                    headers={"Content-Type": content_type, "Content-Length": str(total)},
                    timeout=300,
                )

                if not put_resp.is_success:
                    raise RuntimeError(
                        f"Upload {os.path.basename(upload_path)}: {put_resp.status_code} {put_resp.text}"
                    )

                # (TODO Is this even necessary anymore now that we have FLAC autoconversion)
                # The Light API has an issue where it won't set title/artist metadata properly
                # when uploading non-mp3 files. Give user list of commands to patch manually after
                # upload since files are still processing and a patch immediately after will fail.
                if content_type != "audio/mpeg":
                    path = os.path.basename(upload_path)
                    tags = File(upload_path, easy=True)
                    title = tags.get("title", ["Unknown"])[0] if tags else "Unknown"
                    artist = tags.get("artist", ["Unknown"])[0] if tags else "Unknown"
                    album = tags.get("album", [""])[0] if tags else ""
                    cmd = f'light music update "{path}" --new-title "{title}" --new-artist "{artist}" --new-album "{album}"'
                    manual_update_cmds.append(cmd)
            finally:
                if tmp_path:
                    os.unlink(tmp_path)

        log.info("All uploads complete")

        if len(manual_update_cmds) > 0:
            log.warning(
                "Manual metadata fixes needed:\n"
                + "\n".join(f"  {cmd} ;" for cmd in manual_update_cmds)
            )

    def update_track_metadata(
        self,
        audio_id: str,
        title: str | None = None,
        artist: str | None = None,
        album: str | None = None,
    ):
        """Update metadata (title, artist, album) for a track.

        Args:
            audio_id: The audio_id for the track to edit.
            title: The new title, or None for no changes.
            artist: The new artist, or None for no changes.
            album: The new album, or None for no changes.
        """
        from open_api_specification_client.types import UNSET

        attrs = PatchApiAudiosAudioIdBodyDataAttributes(
            title=title if title is not None else UNSET,
            artist=artist if artist is not None else UNSET,
        )
        if album is not None:
            attrs["album"] = album

        resp = self._l.call_api(
            patch_api_audios_audio_id.sync_detailed,
            audio_id=audio_id,
            client=self._l._api_client,
            body=PatchApiAudiosAudioIdBody(
                data=PatchApiAudiosAudioIdBodyData(
                    id=audio_id,
                    type_=PatchApiAudiosAudioIdBodyDataType.PLAYLIST_ITEMS,
                    attributes=attrs,
                )
            ),
        )
        self._l._ensure_ok(resp, "update metadata", ok_codes=range(200, 300))

        log.info("Metadata updated")

    def reorder_subset(self, ordered_item_ids: list[str]) -> None:
        """Reorder a subset of tracks among the position slots they currently occupy.

        Args:
            ordered_item_ids: playlist_item_ids in the desired order. Tracks on
                device that match these ids are rearranged among their current
                collective position slots; all other tracks are untouched.
                Any matched tracks not present in ordered_item_ids are appended
                at the end of the subset.
        """
        tracks = self.get_tracks()
        id_to_track = {t.playlist_item_id: t for t in tracks}

        target_set = set(ordered_item_ids)
        slots = [i for i, t in enumerate(tracks) if t.playlist_item_id in target_set]

        in_order_set = set(ordered_item_ids)
        full_order = [iid for iid in ordered_item_ids if iid in id_to_track]
        full_order += [
            t.playlist_item_id
            for t in tracks
            if t.playlist_item_id in target_set
            and t.playlist_item_id not in in_order_set
        ]

        # Build complete final ordering: non-targets keep their slots, targets fill in desired order
        final_order = [t.playlist_item_id for t in tracks]
        for slot, item_id in zip(slots, full_order):
            final_order[slot] = item_id

        self.set_sort_mode(SortMode.RANK)

        original_positions = {t.playlist_item_id: i for i, t in enumerate(tracks)}

        for new_position, item_id in enumerate(final_order):
            if original_positions[item_id] == new_position:
                continue
            track = id_to_track[item_id]
            resp = self._l.call_api(
                patch_api_playlist_items_playlist_item_id.sync_detailed,
                playlist_item_id=track.playlist_item_id,
                client=self._l._api_client,
                body=PatchApiPlaylistItemsPlaylistItemIdBody(
                    data=PatchApiPlaylistItemsPlaylistItemIdBodyData(
                        id=track.playlist_item_id,
                        type_=PatchApiPlaylistItemsPlaylistItemIdBodyDataType.PLAYLIST_ITEMS,
                        attributes=PatchApiPlaylistItemsPlaylistItemIdBodyDataAttributes(
                            position=new_position,
                        ),
                    )
                ),
            )
            self._l._ensure_ok(
                resp, f"reorder_subset position {new_position}", ok_codes=range(200, 300)
            )

    def _apply_sort_positions(self, sorted_tracks: list[LightTrack], original_tracks: list[LightTrack]) -> None:
        """PATCH playlist item positions to match the given sort order."""
        original_positions = {t.audio_id: i for i, t in enumerate(original_tracks)}
        for new_position, track in enumerate(sorted_tracks):
            if original_positions[track.audio_id] == new_position:
                continue
            resp = self._l.call_api(
                patch_api_playlist_items_playlist_item_id.sync_detailed,
                playlist_item_id=track.playlist_item_id,
                client=self._l._api_client,
                body=PatchApiPlaylistItemsPlaylistItemIdBody(
                    data=PatchApiPlaylistItemsPlaylistItemIdBodyData(
                        id=track.playlist_item_id,
                        type_=PatchApiPlaylistItemsPlaylistItemIdBodyDataType.PLAYLIST_ITEMS,
                        attributes=PatchApiPlaylistItemsPlaylistItemIdBodyDataAttributes(
                            position=new_position,
                        ),
                    )
                ),
            )
            self._l._ensure_ok(
                resp, f"Apply sort position {new_position}", ok_codes=range(200, 300)
            )

    def _sort_by_title(self, descending: bool = False) -> None:
        """Sort tracks on device by title.

        The dashboard has no native sort-by-title, so we PATCH the position of
        each track directly.

        Args:
            descending: True to sort descending; False for ascending.

        Note:
            @light - i am begging you... please allow sorting by title. crying emoji
        """
        tracks = self.get_tracks()
        self.set_sort_mode(SortMode.RANK)
        self._apply_sort_positions(
            sorted(tracks, key=lambda t: t.title.casefold(), reverse=descending),
            tracks,
        )

    def _sort_by_artist_album(self, descending: bool = False) -> None:
        """Sort tracks on device by artist, then by album.

        All tracks have a hidden 'album' field. The dashboard has no native sort-by-artist-album,
        so we PATCH the position of each track directly.

        Args:
            descending: True to sort descending; False for ascending.
        """
        tracks = self.get_tracks()
        self.set_sort_mode(SortMode.RANK)
        self._apply_sort_positions(
            sorted(tracks, key=lambda t: (t.artist.casefold(), t.album.casefold()), reverse=descending),
            tracks,
        )
