"""Notes management for Light devices."""

import httpx
import logging
import os
from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING

from open_api_specification_client.api.default import (
    get_api_notes,
    get_api_notes_note_id,
    get_api_notes_note_id_generate_presigned_get_url,
    post_api_notes,
)
from open_api_specification_client.models import (
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


class LightNotes:
    def __init__(self, light: "Light") -> None:
        self._l = light

    def get_note_content(self, note: LightNote) -> bytes:
        """Fetch the content of a note as raw bytes.

        Fetches a fresh presigned GET URL each time (they expire).
        """
        resp = get_api_notes_note_id_generate_presigned_get_url.sync_detailed(
            note_id=note.id,
            client=self._l._api_client,
        )
        if resp.status_code != 200 or resp.parsed is None:
            raise RuntimeError(f"Presigned get URL for {note.id}: {resp.status_code}")

        content_resp = httpx.get(resp.parsed.presigned_get_url, timeout=30)
        if not content_resp.is_success:
            raise RuntimeError(f"Download note {note.id}: {content_resp.status_code}")
        return content_resp.content

    def get_notes(self) -> list["LightNote"]:
        """Fetch metadata for all notes."""
        resp = get_api_notes.sync_detailed(
            client=self._l._api_client,
            device_tool_id=self._l._device_tool_ids["notes"],
        )
        if resp.status_code != 200 or resp.parsed is None:
            raise RuntimeError(f"List notes: {resp.status_code}")

        body = resp.parsed

        return [
            LightNote(
                id=data.id,
                file_id=data.attributes.file_id,
                note_type=data.attributes.note_type,
                title=data.attributes.title,
                updated_at=data.attributes.updated_at,
            )
            for data in body.data
        ]

    def get_note_metadata(self, note_id: str) -> "LightNote":
        """Fetch metadata for a single note."""
        resp = get_api_notes_note_id.sync_detailed(
            note_id=note_id,
            client=self._l._api_client,
            device_tool_id=self._l._device_tool_ids["notes"],
        )
        if resp.status_code != 200 or resp.parsed is None:
            raise RuntimeError(f"Fetching note {note_id}: {resp.status_code}")

        body = resp.parsed
        return LightNote(
            id=body.data.id,
            file_id=body.data.attributes.file_id,
            note_type=body.data.attributes.note_type,
            title=body.data.attributes.title,
            updated_at=body.data.attributes.updated_at,
        )

    def download_notes(self, dest: str) -> None:
        """Download all notes to dest directory.

        Text notes saved as .txt, audio notes saved as .m4a.
        """
        os.makedirs(dest, exist_ok=True)

        notes = self.get_notes()
        title_counts = Counter(note.title for note in notes)

        for note in notes:
            if note.title and title_counts[note.title] == 1:
                slug = note.title
            else:
                slug = f"{note.title}_{note.updated_at}" if note.title else note.id

            content = self.get_note_content(note)

            if note.note_type == "audio":
                path = os.path.join(dest, f"{slug}.m4a")
                with open(path, "wb") as f:
                    f.write(content)
            else:
                path = os.path.join(dest, f"{slug}.txt")
                with open(path, "w") as f:
                    f.write(content.decode())

            log.info(f"Saved {path}")

    def create_text_note(
        self, title: str, content: str, content_is_path: bool = False
    ) -> None:
        """Create a new text note.

        Args:
            title: The title of the note to create.
            content: Note content, or a file path if content_is_path is True.
            content_is_path: If True, read content from the given path.
        """
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
        if resp.status_code not in (200, 201) or resp.parsed is None:
            raise RuntimeError(f"Creating note: {resp.status_code}")

        presigned_url = resp.parsed.included[0].attributes.presigned_url

        if content_is_path:
            with open(content) as f:
                _content = f.read()
        else:
            _content = content

        body = _content.encode() if isinstance(_content, str) else _content
        put_resp = httpx.put(presigned_url, content=body, timeout=30)
        if not put_resp.is_success:
            raise RuntimeError(f"Upload note content: {put_resp.status_code}")

        log.info("Note saved")

    def update_note_content(self, note: "LightNote", content: bytes) -> None:
        """Overwrite the content of an existing text note via its presigned upload URL."""
        from open_api_specification_client.api.default import get_api_notes_note_id_generate_presigned_put_url
        resp = self._l.call_api(
            get_api_notes_note_id_generate_presigned_put_url.sync_detailed,
            client=self._l._api_client,
            note_id=note.id,
        )
        if resp.status_code != 200 or resp.parsed is None:
            raise RuntimeError(f"Presigned put URL for {note.id}: {resp.status_code}")
        put_resp = httpx.put(resp.parsed.presigned_put_url, content=content, timeout=30)
        if not put_resp.is_success:
            raise RuntimeError(f"Upload note content: {put_resp.status_code}")
        log.info(f"Note {note.id} updated")
