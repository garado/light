"""Notes management for Light devices."""

import base64
import dataclasses
import httpx
import logging
import os
from collections import Counter
from dataclasses import dataclass
from typing import Callable, TYPE_CHECKING

from light_api import cache

from open_api_specification_client.api.default import (
    delete_api_notes_note_id,
    get_api_notes,
    get_api_notes_note_id,
    get_api_notes_note_id_generate_presigned_get_url,
    get_api_notes_note_id_generate_presigned_put_url,
    patch_api_notes_note_id,
    post_api_notes,
)
from open_api_specification_client.models import (
    PatchApiNotesNoteIdBody,
    PatchApiNotesNoteIdBodyData,
    PatchApiNotesNoteIdBodyDataAttributes,
    PatchApiNotesNoteIdBodyDataRelationships,
    PatchApiNotesNoteIdBodyDataRelationshipsFile,
    PatchApiNotesNoteIdBodyDataRelationshipsFileData,
    PostApiNotesBody,
    PostApiNotesBodyData,
    PostApiNotesBodyDataAttributes,
    PostApiNotesBodyDataAttributesNoteType,
    PostApiNotesBodyDataType,
)

if TYPE_CHECKING:
    from light_api.client import Light

log = logging.getLogger(f"light.{__name__}")


@dataclass
class LightNote:
    id: str
    file_id: str
    note_type: str
    title: str
    updated_at: str


def _make_light_note(data) -> "LightNote":
    return LightNote(
        id=data.id,
        file_id=data.attributes.file_id,
        note_type=data.attributes.note_type,
        title=data.attributes.title,
        updated_at=data.attributes.updated_at,
    )


@dataclass
class NoteContentResult:
    id: str
    title: str
    note_type: str
    updated_at: str
    content: str | None
    saved_to: str | None


@dataclass
class NoteDownloadResult:
    note_id: str
    title: str
    path: str | None
    success: bool
    error: str | None


class LightNotes:
    def __init__(self, light: "Light") -> None:
        self._l = light

    def get_note_content(self, note: LightNote) -> bytes:
        """Fetch the content of a note as raw bytes.

        Fetches a fresh presigned GET URL each time (they expire fast), unless cached.
        """
        if self._l._cache_enabled:
            cached = cache.load(
                cache.CacheModule.NOTES, self._l._api_token, key=note.id
            )
            if cached is not None:
                return base64.b64decode(cached)

        resp = get_api_notes_note_id_generate_presigned_get_url.sync_detailed(
            note_id=note.id,
            client=self._l._api_client,
        )
        self._l._ensure_ok(
            resp, f"Presigned get URL for {note.id}", require_parsed=True
        )

        content_resp = httpx.get(resp.parsed.presigned_get_url, timeout=30)
        if not content_resp.is_success:
            raise RuntimeError(f"Download note {note.id}: {content_resp.status_code}")
        content = content_resp.content

        if self._l._cache_enabled:
            cache.save(
                cache.CacheModule.NOTES,
                self._l._api_token,
                base64.b64encode(content).decode(),
                key=note.id,
            )

        return content

    def get_notes(self) -> list["LightNote"]:
        """Fetch metadata for all notes."""
        if self._l._cache_enabled:
            cached = cache.load(cache.CacheModule.NOTES, self._l._api_token)
            if cached is not None:
                return [LightNote(**d) for d in cached]

        resp = get_api_notes.sync_detailed(
            client=self._l._api_client,
            device_tool_id=self._l._device_tool_ids["notes"],
        )
        body = self._l._ensure_ok(resp, "List notes", require_parsed=True)

        notes = [_make_light_note(data) for data in body.data]

        if self._l._cache_enabled:
            cache.save(
                cache.CacheModule.NOTES,
                self._l._api_token,
                [dataclasses.asdict(n) for n in notes],
            )

        return notes

    def get_note_metadata(self, note_id: str) -> "LightNote":
        """Fetch metadata for a single note."""
        resp = get_api_notes_note_id.sync_detailed(
            note_id=note_id,
            client=self._l._api_client,
            device_tool_id=self._l._device_tool_ids["notes"],
        )
        self._l._ensure_ok(resp, f"Fetching note {note_id}", require_parsed=True)

        return _make_light_note(resp.parsed.data)

    def download_notes(
        self,
        dest: str,
        on_progress: Callable[[int, int, "LightNote"], None] | None = None,
    ) -> list[NoteDownloadResult]:
        """Download all notes to dest directory.

        Text notes are saved as .txt and audio notes saved as .m4a.

        Args:
            dest: Directory to save notes into.
            on_progress: Called as `on_progress(index, total, note)` before each note
                starts downloading, 1-indexed.

        Returns:
            A list of per-note results. `path` is None and `error` is set when
            that note failed.
        """
        os.makedirs(dest, exist_ok=True)

        notes = self.get_notes()
        title_counts = Counter(note.title for note in notes)
        total = len(notes)

        results = []
        for i, note in enumerate(notes, 1):
            if on_progress:
                on_progress(i, total, note)

            if note.title and title_counts[note.title] == 1:
                slug = note.title
            else:
                slug = f"{note.title}_{note.updated_at}" if note.title else note.id

            ext = "m4a" if note.note_type == "audio" else "txt"
            path = os.path.join(dest, f"{slug}.{ext}")

            try:
                content = self.get_note_content(note)
                if note.note_type == "audio":
                    with open(path, "wb") as f:
                        f.write(content)
                else:
                    with open(path, "w") as f:
                        f.write(content.decode())
                log.info(f"Saved {path}")
                results.append(
                    NoteDownloadResult(
                        note_id=note.id,
                        title=note.title,
                        path=path,
                        success=True,
                        error=None,
                    )
                )
            except RuntimeError as e:
                results.append(
                    NoteDownloadResult(
                        note_id=note.id,
                        title=note.title,
                        path=None,
                        success=False,
                        error=str(e),
                    )
                )

        return results

    def create_text_note(
        self, title: str, content: str, content_is_path: bool = False
    ) -> "LightNote":
        """Create a new text note and return the resulting LightNote."""
        resp = post_api_notes.sync_detailed(
            client=self._l._api_client,
            body=PostApiNotesBody(
                data=PostApiNotesBodyData(
                    type_=PostApiNotesBodyDataType.NOTES,
                    attributes=PostApiNotesBodyDataAttributes(
                        device_tool_id=self._l._device_tool_ids["notes"],
                        filename="note.txt",
                        note_type=PostApiNotesBodyDataAttributesNoteType.TEXT,
                        title=title,
                    ),
                )
            ),
        )
        parsed = self._l._ensure_ok(
            resp, "Creating note", ok_codes=(200, 201), require_parsed=True
        )

        presigned_url = parsed.included[0].attributes.presigned_url

        if content_is_path:
            with open(content) as f:
                _content = f.read()
        else:
            _content = content

        body = _content.encode() if isinstance(_content, str) else _content
        put_resp = httpx.put(presigned_url, content=body, timeout=30)
        if not put_resp.is_success:
            raise RuntimeError(f"Upload note content: {put_resp.status_code}")

        note = _make_light_note(parsed.data)
        log.info(f"Note {note.id} created")

        cache.invalidate(cache.CacheModule.NOTES)

        return note

    def update_note_content(self, note: LightNote, content: bytes) -> None:
        """Overwrite the content of an existing text note via its presigned upload URL."""
        resp = self._l.call_api(
            get_api_notes_note_id_generate_presigned_put_url.sync_detailed,
            client=self._l._api_client,
            note_id=note.id,
        )
        self._l._ensure_ok(
            resp, f"Presigned put URL for {note.id}", require_parsed=True
        )
        put_resp = httpx.put(resp.parsed.presigned_put_url, content=content, timeout=30)
        if not put_resp.is_success:
            raise RuntimeError(f"Upload note content: {put_resp.status_code}")
        log.info(f"Note {note.id} updated")

        # invalidate the list too: `updated_at` (shown there) just changed
        cache.invalidate(cache.CacheModule.NOTES)
        cache.invalidate(cache.CacheModule.NOTES, key=note.id)

    def update_note_title(self, note: LightNote, title: str) -> None:
        """Update the title of an existing note."""
        resp = self._l.call_api(
            patch_api_notes_note_id.sync_detailed,
            client=self._l._api_client,
            note_id=note.id,
            body=PatchApiNotesNoteIdBody(
                data=PatchApiNotesNoteIdBodyData(
                    id=note.id,
                    type_="notes",
                    attributes=PatchApiNotesNoteIdBodyDataAttributes(
                        title=title,
                        updated_at=note.updated_at,
                        note_type=note.note_type,
                    ),
                    relationships=PatchApiNotesNoteIdBodyDataRelationships(
                        file=PatchApiNotesNoteIdBodyDataRelationshipsFile(
                            data=PatchApiNotesNoteIdBodyDataRelationshipsFileData(
                                type_="files",
                                id=note.file_id,
                            )
                        )
                    ),
                )
            ),
        )
        self._l._ensure_ok(resp, "Update note title", ok_codes=(200, 204))
        note.title = title
        log.info(f"Note {note.id} title updated to {title!r}")

        cache.invalidate(cache.CacheModule.NOTES)

    def delete_note(self, note_id: str) -> None:
        """Delete a note."""
        resp = self._l.call_api(
            delete_api_notes_note_id.sync_detailed,
            client=self._l._api_client,
            note_id=note_id,
        )
        self._l._ensure_ok(resp, "Delete note", ok_codes=(200, 204))
        log.info(f"Note {note_id} deleted")

        cache.invalidate(cache.CacheModule.NOTES)
        cache.invalidate(cache.CacheModule.NOTES, key=note_id)
