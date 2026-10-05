"""Tests for light_api.notes."""

import pytest
import respx
import httpx

from light_api.notes import LightNote

from helpers import API, make_light


def make_note(overrides: dict | None = None) -> LightNote:
    data = dict(id="note-1", file_id="file-1", note_type="text", title="old title", updated_at="2026-01-01T00:00:00")
    if overrides:
        data.update(overrides)
    return LightNote(**data)


class TestGetNotes:
    @respx.mock
    def test_returns_list_of_light_notes(self, f_devices, f_tools, f_notes):
        respx.get(f"{API}/api/devices").mock(return_value=httpx.Response(200, json=f_devices))
        respx.get(f"{API}/api/tools").mock(return_value=httpx.Response(200, json=f_tools))
        respx.get(f"{API}/api/notes").mock(return_value=httpx.Response(200, json=f_notes))

        light = make_light()
        light._fetch_device_tool_ids()
        notes = light.notes.get_notes()

        assert isinstance(notes, list)
        assert len(notes) == len(f_notes["data"])
        assert all(isinstance(n, LightNote) for n in notes)

    @respx.mock
    def test_note_fields_match_fixture(self, f_devices, f_tools, f_notes):
        respx.get(f"{API}/api/devices").mock(return_value=httpx.Response(200, json=f_devices))
        respx.get(f"{API}/api/tools").mock(return_value=httpx.Response(200, json=f_tools))
        respx.get(f"{API}/api/notes").mock(return_value=httpx.Response(200, json=f_notes))

        light = make_light()
        light._fetch_device_tool_ids()
        notes = light.notes.get_notes()

        fixture_ids = {item["id"] for item in f_notes["data"]}
        for note in notes:
            assert note.id in fixture_ids
            assert note.note_type in ("text", "audio")
            assert isinstance(note.title, str)
            assert isinstance(note.updated_at, str)

    @respx.mock
    def test_raises_on_error_response(self, f_devices, f_tools):
        respx.get(f"{API}/api/devices").mock(return_value=httpx.Response(200, json=f_devices))
        respx.get(f"{API}/api/tools").mock(return_value=httpx.Response(200, json=f_tools))
        respx.get(f"{API}/api/notes").mock(return_value=httpx.Response(403, json={}))

        light = make_light()
        light._fetch_device_tool_ids()
        with pytest.raises(RuntimeError, match="403"):
            light.notes.get_notes()


class TestUpdateNoteTitle:
    @respx.mock
    def test_updates_note_title(self, f_devices, f_tools):
        respx.get(f"{API}/api/devices").mock(return_value=httpx.Response(200, json=f_devices))
        respx.get(f"{API}/api/tools").mock(return_value=httpx.Response(200, json=f_tools))
        respx.patch(f"{API}/api/notes/note-1").mock(return_value=httpx.Response(200, json={
            "data": {"id": "note-1", "type": "notes", "attributes": {"title": "new title"}}
        }))

        light = make_light()
        light._fetch_device_tool_ids()
        note = make_note()
        light.notes.update_note_title(note, "new title")

        assert note.title == "new title"

    @respx.mock
    def test_raises_on_error_response(self, f_devices, f_tools):
        respx.get(f"{API}/api/devices").mock(return_value=httpx.Response(200, json=f_devices))
        respx.get(f"{API}/api/tools").mock(return_value=httpx.Response(200, json=f_tools))
        respx.patch(f"{API}/api/notes/note-1").mock(return_value=httpx.Response(422, json={}))

        light = make_light()
        light._fetch_device_tool_ids()
        with pytest.raises(RuntimeError, match="422"):
            light.notes.update_note_title(make_note(), "new title")


class TestDeleteNote:
    @respx.mock
    def test_succeeds_on_204(self, f_devices, f_tools):
        respx.get(f"{API}/api/devices").mock(return_value=httpx.Response(200, json=f_devices))
        respx.get(f"{API}/api/tools").mock(return_value=httpx.Response(200, json=f_tools))
        respx.delete(f"{API}/api/notes/note-1").mock(return_value=httpx.Response(204))

        light = make_light()
        light._fetch_device_tool_ids()
        light.notes.delete_note("note-1")  # should not raise

    @respx.mock
    def test_raises_on_error_response(self, f_devices, f_tools):
        respx.get(f"{API}/api/devices").mock(return_value=httpx.Response(200, json=f_devices))
        respx.get(f"{API}/api/tools").mock(return_value=httpx.Response(200, json=f_tools))
        respx.delete(f"{API}/api/notes/note-1").mock(return_value=httpx.Response(404, json={}))

        light = make_light()
        light._fetch_device_tool_ids()
        with pytest.raises(RuntimeError, match="404"):
            light.notes.delete_note("note-1")


class TestCreateTextNote:
    def _create_response(self) -> dict:
        return {
            "data": {
                "id": "new-note-1",
                "type": "notes",
                "attributes": {
                    "device_tool_id": "dtid-1",
                    "file_id": "new-file-1",
                    "note_type": "text",
                    "title": "my note",
                    "updated_at": "2026-01-01T00:00:00",
                },
                "relationships": {"file": {"data": {"id": "new-file-1", "type": "files"}}},
            },
            "included": [
                {"id": "new-file-1", "type": "files", "attributes": {
                    "presigned_url": "https://s3.example.com/upload",
                    "bucket": "light-two-api-production",
                    "key": "files/new-file-1/note.txt",
                    "content_type": "text/plain",
                    "secret": None,
                    "uploaded_at": None,
                }}
            ],
            "jsonapi": {"version": "1.0"},
        }

    @respx.mock
    def test_returns_light_note(self, f_devices, f_tools):
        respx.get(f"{API}/api/devices").mock(return_value=httpx.Response(200, json=f_devices))
        respx.get(f"{API}/api/tools").mock(return_value=httpx.Response(200, json=f_tools))
        respx.post(f"{API}/api/notes").mock(return_value=httpx.Response(201, json=self._create_response()))
        respx.put("https://s3.example.com/upload").mock(return_value=httpx.Response(200))

        light = make_light()
        light._fetch_device_tool_ids()
        note = light.notes.create_text_note("my note", "hello world")

        assert isinstance(note, LightNote)
        assert note.id == "new-note-1"
        assert note.title == "my note"
        assert note.file_id == "new-file-1"

    @respx.mock
    def test_raises_on_api_error(self, f_devices, f_tools):
        respx.get(f"{API}/api/devices").mock(return_value=httpx.Response(200, json=f_devices))
        respx.get(f"{API}/api/tools").mock(return_value=httpx.Response(200, json=f_tools))
        respx.post(f"{API}/api/notes").mock(return_value=httpx.Response(500, json={}))

        light = make_light()
        light._fetch_device_tool_ids()
        with pytest.raises(RuntimeError, match="500"):
            light.notes.create_text_note("my note", "hello world")

    @respx.mock
    def test_raises_on_upload_error(self, f_devices, f_tools):
        respx.get(f"{API}/api/devices").mock(return_value=httpx.Response(200, json=f_devices))
        respx.get(f"{API}/api/tools").mock(return_value=httpx.Response(200, json=f_tools))
        respx.post(f"{API}/api/notes").mock(return_value=httpx.Response(201, json=self._create_response()))
        respx.put("https://s3.example.com/upload").mock(return_value=httpx.Response(403))

        light = make_light()
        light._fetch_device_tool_ids()
        with pytest.raises(RuntimeError, match="403"):
            light.notes.create_text_note("my note", "hello world")
