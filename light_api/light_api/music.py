"""Music management for Light devices."""

import dataclasses
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

from light_api import cache
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
    filename: str  # original uploaded filename


@dataclass
class UploadResult:
    file: str
    audio_id: str | None
    success: bool
    error: str | None


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
    
    def _set_sort_mode(self, sort_mode: SortMode, invalidate_cache: bool = True):
        """Set sort mode.

        This private method offers the the ability to control cache invalidation.
        The public method is `set_sort_mode`, which always invalidates cache.

        Args:
            sort_mode: The new sort mode to set.
            invalidate_cache: Whether the cache should be invalidated.
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

        cache.invalidate(cache.CacheModule.MUSIC)

    def set_sort_mode(self, sort_mode: SortMode):
        """Set sort mode.

        Args:
            sort_mode: The new sort mode to set.
        """
        self._set_sort_mode(sort_mode, invalidate_cache=True)
    
    def get_tracks(self) -> list[LightTrack]:
        """Fetch list of all tracks on the device.

        Returns:
            List of LightTracks in the current playlist order.
        """
        if self._l._cache_enabled:
            cached = cache.load(cache.CacheModule.MUSIC, self._l._api_token)
            if cached is not None:
                return [LightTrack(**d) for d in cached]

        resp = self._l.call_api(
            get_api_playlist_items.sync_detailed,
            client=self._l._api_client,
            playlist_ids=self._l._playlist_id,
            device_tool_id=self._l._device_tool_ids["music"],
        )
        body = self._l._ensure_ok(resp, "Get tracks", require_parsed=True)

        # Light returns 2 separate collections:
        # - body.data[] - a track's position + a reference to its associated body.included member
        # - body.included - full track metadata + file storage info ("attributes")
        # we need to reassemble the info in these into 1 list[LightTracks]

        if not body.data:
            tracks = []
        else:
            # build dict to look up attributes from file id
            file_attrs = {
                item.id: item.attributes for item in body.included if item.type_ == "files"
            }

            # build dict to look up attrs, file id from audio id
            audio_info = {
                item.id: {
                    "attrs": item.attributes,
                    "file_id": item.relationships.processed_file.data.id,
                }
                for item in body.included
                if item.type_ == "audios"
            }

            # order tracks
            items = sorted(body.data, key=lambda x: x.attributes.position)

            tracks = [
                LightTrack(
                    playlist_item_id=item.id,
                    audio_id=(audio_id := item.relationships.audio.data.id),
                    title=audio_info[audio_id]["attrs"].title or "",
                    artist=audio_info[audio_id]["attrs"].artist or "",
                    album=audio_info[audio_id]["attrs"].album or "",
                    filename=os.path.basename(
                        file_attrs[audio_info[audio_id]["file_id"]].key or ""
                    ),
                )
                for item in items
            ]

        if self._l._cache_enabled:
            cache.save(
                cache.CacheModule.MUSIC,
                self._l._api_token,
                [dataclasses.asdict(t) for t in tracks],
            )

        return tracks

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

        cache.invalidate(cache.CacheModule.MUSIC)

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

        if tracks_deleted > 0:
            cache.invalidate(cache.CacheModule.MUSIC)

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
        """Return the subset of files to upload and the subset of tracks to overwrite after
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

    @staticmethod
    def filter_valid_tracks(files: list[str]) -> tuple[list[str], list[str]]:
        """Verify validity of audio files, returning (valid, invalid)."""
        valid = []
        invalid = []
        for file_path in files:
            (valid if os.path.exists(file_path) else invalid).append(file_path)
        return valid, invalid

    _MUSIC_EXTENSIONS = {".mp3", ".flac", ".m4a", ".wav"}
    CONVERTIBLE_EXTENSIONS = {".flac"}

    @classmethod
    def is_convertible(cls, file_path: str) -> bool:
        """True if file_path is in a format that gets converted to MP3 before upload."""
        return os.path.splitext(file_path)[1].lower() in cls.CONVERTIBLE_EXTENSIONS

    @classmethod
    def expand_music_paths(cls, paths: list[str], recursive: bool = False) -> list[str]:
        """Expand any directories in `paths` into the audio files they contain.

        Non-directory entries (individual file paths) pass through unchanged.
        Directories are expanded top-level only unless recursive=True.
        """
        files = []
        for path in paths:
            if not os.path.isdir(path):
                files.append(path)
                continue

            if recursive:
                for root, _dirs, filenames in os.walk(path):
                    for filename in sorted(filenames):
                        if os.path.splitext(filename)[1].lower() in cls._MUSIC_EXTENSIONS:
                            files.append(os.path.join(root, filename))
            else:
                for filename in sorted(os.listdir(path)):
                    full = os.path.join(path, filename)
                    if os.path.isfile(full) and os.path.splitext(filename)[1].lower() in cls._MUSIC_EXTENSIONS:
                        files.append(full)

        return files

    def upload_tracks(
        self,
        files: list[str],
        allow_duplicates: bool = False,
        overwrite: bool = False,
        convert_flac: bool = True,
        on_progress: "Callable[[str, int, int], None] | None" = None,
        on_convert: "Callable[[str], None] | None" = None,
        on_file_start: "Callable[[int, int, str], None] | None" = None,
    ) -> list[UploadResult]:
        """Upload tracks to device.

        Args:
            files: List of paths to audio files to upload.
            allow_duplicates: If True, skip duplicate checking entirely and always upload,
                               potentially creating multiple tracks with the same title/artist.
            overwrite: If True, delete a file's matching existing track (if any) before
                       uploading it. If False (default), files matching an existing track
                       are skipped instead, leaving the existing track untouched.
            on_convert: Called with a file's path right before it is converted to MP3.
            on_file_start: Called with (index, total, file_path) - 1-based index into
                            the files actually being uploaded - right before each file
                            starts processing (before conversion, if any).

        Returns:
            A list of per-file results, one per file attempted.
        """
        if overwrite and allow_duplicates:
            raise ValueError("overwrite and allow_duplicates are mutually exclusive")

        valid_files, invalid_files = self.filter_valid_tracks(files)
        for file_path in invalid_files:
            log.warning(f"File not found, skipping: {file_path}")

        to_upload, to_delete = self._resolve_upload_plan(
            valid_files, allow_duplicates, overwrite
        )

        if to_delete:
            audio_ids = {t.audio_id for t in to_delete}
            self.delete_tracks_predicate(lambda t: t.audio_id in audio_ids)

        total_files = len(to_upload)
        results = []
        for index, file_path in enumerate(to_upload, 1):
            log.info(f"Uploading {file_path}")
            if on_file_start:
                on_file_start(index, total_files, file_path)

            tmp_path = None
            try:
                if convert_flac and self.is_convertible(file_path):
                    log.info(f"Converting {file_path} to MP3")
                    if on_convert:
                        on_convert(file_path)
                    tmp_path = _flac_to_mp3(file_path)
                    upload_path = tmp_path
                    server_filename = os.path.splitext(os.path.basename(file_path))[0] + ".mp3"
                    display_name = f"{server_filename} (converted)"
                else:
                    upload_path = file_path
                    server_filename = os.path.basename(file_path)
                    display_name = server_filename

                create_resp = self._l.call_api(
                    post_api_audios.sync_detailed,
                    client=self._l._api_client,
                    body=PostApiAudiosBody(
                        data=PostApiAudiosBodyData(
                            type_=PostApiAudiosBodyDataType.AUDIOS,
                            attributes=PostApiAudiosBodyDataAttributes(
                                filename=server_filename,
                                device_tool_id=self._l._device_tool_ids["music"],
                            ),
                        )
                    ),
                )
                created = self._l._ensure_ok(
                    create_resp,
                    f"Create audio record for {server_filename}",
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
                    content=_chunks(upload_path, total, display_name),
                    headers={"Content-Type": content_type, "Content-Length": str(total)},
                    timeout=300,
                )

                if not put_resp.is_success:
                    raise RuntimeError(
                        f"Upload {os.path.basename(upload_path)}: {put_resp.status_code} {put_resp.text}"
                    )

                results.append(
                    UploadResult(
                        file=file_path, audio_id=created.data.id, success=True, error=None
                    )
                )
            except RuntimeError as e:
                results.append(
                    UploadResult(file=file_path, audio_id=None, success=False, error=str(e))
                )
            finally:
                if tmp_path:
                    os.unlink(tmp_path)

        log.info("All uploads complete")

        if any(r.success for r in results):
            cache.invalidate(cache.CacheModule.MUSIC)

        return results

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

        cache.invalidate(cache.CacheModule.MUSIC)

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

        self._set_sort_mode(SortMode.RANK, invalidate_cache=False)

        original_positions = {t.playlist_item_id: i for i, t in enumerate(tracks)}

        try:
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
        except Exception:
            cache.invalidate(cache.CacheModule.MUSIC)
            raise

        # If this is reached, every PATCH above succeeded, so the new track ordering is known.
        # Update the cache in-place to avoid a needless refetch.
        if self._l._cache_enabled:
            reordered = [id_to_track[iid] for iid in final_order]
            cache.save(
                cache.CacheModule.MUSIC,
                self._l._api_token,
                [dataclasses.asdict(t) for t in reordered],
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
