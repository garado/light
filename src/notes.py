"""Notes management for Light devices."""

import logging
import os
from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING

from rich.console import Console

import endpoints

if TYPE_CHECKING:
    from core import Light

console = Console()
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

    def _note_from_data(self, data: dict, included: dict) -> "LightNote":
        """Build a LightNote from a data item and its included file entry."""
        return LightNote(
            id=data["id"],
            file_id=data["attributes"]["file_id"],
            note_type=data["attributes"]["note_type"],
            title=data["attributes"]["title"],
            updated_at=data["attributes"]["updated_at"],
            presigned_url=included["attributes"]["presigned_url"],
        )

    def get_note_content(self, note: LightNote) -> bytes:
        """Fetch the content of a note as raw bytes.

        Fetches a fresh presigned GET URL each time (they expire).
        """
        resp = self._l._request(
            endpoints.note_presigned_get_url(note.id),
        )

        self._l._check_response(resp, f"presigned get url for {note.id}")
        presigned_get_url = resp.json()["presigned_get_url"]

        content_resp = self._l._fetch(presigned_get_url, method="GET")

        return content_resp.body()

    def get_notes(self) -> list["LightNote"]:
        """Fetch metadata for all notes."""
        device_tool_id = self._ensure_device_tool_id()

        resp = self._l._request(
            f"{endpoints.NOTES}?device_tool_id={device_tool_id}",
        )
        self._l._check_response(resp, "list notes")

        json = resp.json()
        assert len(json["data"]) == len(json["included"])

        return [
            self._note_from_data(data, included)
            for data, included in zip(json["data"], json["included"])
        ]

    def get_note_metadata(self, note_id: str) -> "LightNote":
        """Fetch metadata for a single note."""
        self._ensure_device_tool_id()

        resp = self._l._request(endpoints.note(note_id), method="GET")
        self._l._check_response(resp, f"fetching note {note_id}")

        json = resp.json()
        return self._note_from_data(json["data"], json["included"][0])

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

            console.print(f"[green]Saved:[/green] {path}")

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

        resp = self._l._request(
            endpoints.NOTES,
            method="POST",
            data={
                "data": {
                    "attributes": {
                        "device_tool_id": device_tool_id,
                        "filename": "note.txt",
                        "note_type": "text",
                        "title": title,
                    },
                    "type": "notes",
                }
            },
        )
        self._l._check_response(resp, "creating note")

        presigned_url = resp.json()["included"][0]["attributes"]["presigned_url"]

        if content_is_path:
            with open(content) as f:
                _content = f.read()
        else:
            _content = content

        self._l._fetch(presigned_url, method="PUT", data=_content)

        console.print(f"[green]Saved note successfully[/green]")
