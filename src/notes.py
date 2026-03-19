"""Notes management for Light devices."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any
from rich.console import Console

if TYPE_CHECKING:
    from core import Light

console = Console()

API_BASE = "https://production.lightphonecloud.com"
NOTES_BASE = "light-two-api-production.nyc3.digitaloceanspaces.com"


@dataclass
class LightNote:
    id: str  # for making call to get presigned GET url
    file_id: str  # for making call to fetch content
    presigned_url: str  # ???
    presigned_get_url: str  # ???
    note_type: str
    title: str
    content: Any
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

    def get_notes(self) -> list[LightNote]:
        """Fetch all notes, downloading content via presigned URLs."""
        print("getting notes")

        device_tool_id = self._ensure_device_tool_id()

        resp = self._l._request(
            f"{API_BASE}/api/notes?device_tool_id={device_tool_id}",
        )

        self._l._check_response(resp, "list notes")

        json = resp.json()
        assert len(json["data"]) == len(json["included"])
        notes_count = len(json["data"])

        print(f"{notes_count} notes")

        notes = []

        for i in range(notes_count):
            id = json["data"][i]["id"]
            file_id = json["data"][i]["attributes"]["file_id"]
            note_type = json["data"][i]["attributes"]["note_type"]
            title = json["data"][i]["attributes"]["title"]
            updated_at = json["data"][i]["attributes"]["updated_at"]

            presigned_url = json["included"][i]["attributes"]["presigned_url"]

            # presigned get url is a separate call
            resp = self._l._request(
                f"{API_BASE}/api/notes/{id}/generate_presigned_get_url",
            )
            self._l._check_response(resp, "presigned get url")
            presigned_get_url = resp.json()["presigned_get_url"]

            # getting content is a separate call
            if note_type == "text":
                resp = self._l._page.request.fetch(
                    presigned_get_url,
                    headers={},
                    method="GET",
                )
                content = resp.text()
            else:
                content = None

            note = LightNote(
                id=id,
                file_id=file_id,
                note_type=note_type,
                title=title,
                updated_at=updated_at,
                presigned_url=presigned_url,
                presigned_get_url=presigned_get_url,
                content=content,
            )

            notes.append(note)

        print(notes)

        return notes
