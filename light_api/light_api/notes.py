"""Notes management for Light devices."""

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
    presigned_url: str  # PUT URL for uploading content
    note_type: str
    title: str
    updated_at: str


class LightNotes:
    def __init__(self, light: "Light") -> None:
        self._l = light

    def _ensure_device_tool_id(self) -> str:
        if self._l._notes_device_tool_id is None:
            self._l._fetch_notes_device_tool_id()
            self._l._save_cache()
        assert self._l._notes_device_tool_id is not None
        return self._l._notes_device_tool_id

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

        content_resp = self._l._fetch(resp.parsed.presigned_get_url, method="GET")
        return content_resp.body()

    def get_notes(self) -> list["LightNote"]:
        """Fetch metadata for all notes."""
        device_tool_id = self._ensure_device_tool_id()

        resp = get_api_notes.sync_detailed(
            client=self._l._api_client,
            device_tool_id=device_tool_id,
        )
        if resp.status_code != 200 or resp.parsed is None:
            raise RuntimeError(f"List notes: {resp.status_code}")

        body = resp.parsed
        if len(body.data) != len(body.included):
            raise RuntimeError(
                f"Expected {len(body.data)} included items, got {len(body.included)}"
            )

        return [
            LightNote(
                id=data.id,
                file_id=data.attributes.file_id,
                note_type=data.attributes.note_type,
                title=data.attributes.title,
                updated_at=data.attributes.updated_at,
                presigned_url=included.attributes.presigned_url,
            )
            for data, included in zip(body.data, body.included)
        ]

    def get_note_metadata(self, note_id: str) -> "LightNote":
        """Fetch metadata for a single note."""
        device_tool_id = self._ensure_device_tool_id()

        resp = get_api_notes_note_id.sync_detailed(
            note_id=note_id,
            client=self._l._api_client,
            device_tool_id=device_tool_id,
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
            presigned_url=body.included[0].attributes.presigned_url,
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
        device_tool_id = self._ensure_device_tool_id()

        resp = post_api_notes.sync_detailed(
            client=self._l._api_client,
            body=PostApiNotesBody(
                data=PostApiNotesBodyData(
                    type_=PostApiNotesBodyDataType.NOTES,
                    attributes=PostApiNotesBodyDataAttributes(
                        device_tool_id=device_tool_id,
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

        self._l._fetch(presigned_url, method="PUT", data=_content)

        log.info("Note saved")
