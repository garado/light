"""Tests for light_api parsing logic, played back against fixture JSON."""

import json
import pytest
import respx
import httpx
from unittest.mock import patch

from light_api.client import Light
from light_api.notes import LightNote
from light_api.music import LightTrack

API = "https://production.lightphonecloud.com"


def make_light(phone: str | None = None, device_id: str | None = None) -> Light:
    """Return a Light instance with auth bypassed."""
    from open_api_specification_client.client import AuthenticatedClient
    from light_api.music import LightMusic
    from light_api.notes import LightNotes
    from light_api.tools import LightTools
    from light_api.podcast import LightPodcasts
    light = Light(email="test@example.com", password="test", phone=phone, device_id=device_id)
    light._api_token = "fake-token"
    light._api_client = AuthenticatedClient(base_url=API, token="fake-token")
    light.music = LightMusic(light)
    light.notes = LightNotes(light)
    light.tools = LightTools(light)
    light.podcast = LightPodcasts(light)
    return light


class TestFetchDeviceToolIds:
    @respx.mock
    def test_populates_all_tool_ids(self, f_devices, f_tools):
        device_id = f_devices["data"][0]["id"]
        respx.get(f"{API}/api/devices").mock(return_value=httpx.Response(200, json=f_devices))
        respx.get(f"{API}/api/tools").mock(return_value=httpx.Response(200, json=f_tools))

        light = make_light()
        light._fetch_device_tool_ids()

        assert "notes" in light._device_tool_ids
        assert "music" in light._device_tool_ids or "podcast" in light._device_tool_ids
        for v in light._device_tool_ids.values():
            assert isinstance(v, str) and len(v) > 0

    @respx.mock
    def test_device_tool_ids_match_fixture(self, f_devices, f_tools):
        """Each stored device_tool_id must appear in the fixture's included items."""
        respx.get(f"{API}/api/devices").mock(return_value=httpx.Response(200, json=f_devices))
        respx.get(f"{API}/api/tools").mock(return_value=httpx.Response(200, json=f_tools))

        light = make_light()
        light._fetch_device_tool_ids()

        valid_ids = {item["id"] for item in f_devices["included"]}
        for key, val in light._device_tool_ids.items():
            assert val in valid_ids, f"{key} device_tool_id {val!r} not in fixture included ids"


class TestSelectDeviceId:
    """Unit tests for Light._select_device_id, exercised directly against a
    parsed /api/devices response (no HTTP mocking needed)."""

    @staticmethod
    def _parsed(raw: dict):
        from open_api_specification_client.models.get_api_devices_response_200 import (
            GetApiDevicesResponse200,
        )

        return GetApiDevicesResponse200.from_dict(raw)

    def test_single_device_no_selector(self, f_devices):
        light = make_light()
        device_id = light._select_device_id(self._parsed(f_devices))
        assert device_id == f_devices["data"][0]["id"]

    def test_multiple_devices_no_selector_raises(self, f_devices_multi):
        light = make_light()
        with pytest.raises(RuntimeError, match="Multiple devices found"):
            light._select_device_id(self._parsed(f_devices_multi))

    def test_device_id_selects_matching_device(self, f_devices_multi):
        target = f_devices_multi["data"][1]["id"]
        light = make_light(device_id=target)
        assert light._select_device_id(self._parsed(f_devices_multi)) == target

    def test_device_id_no_match_raises(self, f_devices_multi):
        light = make_light(device_id="does-not-exist")
        with pytest.raises(RuntimeError, match="No device found with id"):
            light._select_device_id(self._parsed(f_devices_multi))

    def test_phone_selects_matching_device(self, f_devices_multi):
        # Stored as "+15125550199" - passed with different formatting/no country code.
        light = make_light(phone="(512) 555-0199")
        target = f_devices_multi["data"][1]["id"]
        assert light._select_device_id(self._parsed(f_devices_multi)) == target

    def test_phone_no_match_raises(self, f_devices_multi):
        light = make_light(phone="0000000000")
        with pytest.raises(RuntimeError, match="No device found matching phone number"):
            light._select_device_id(self._parsed(f_devices_multi))


class TestFetchDeviceToolIdsMultiDevice:
    @respx.mock
    def test_only_assigns_tool_ids_for_selected_device(self, f_devices_multi, f_tools):
        target = f_devices_multi["data"][1]["id"]
        respx.get(f"{API}/api/devices").mock(
            return_value=httpx.Response(200, json=f_devices_multi)
        )
        respx.get(f"{API}/api/tools").mock(return_value=httpx.Response(200, json=f_tools))

        light = make_light(device_id=target)
        light._fetch_device_tool_ids()

        other_device_tool_ids = {
            item["id"]
            for item in f_devices_multi["included"]
            if item["type"] == "device_tools"
            and item["relationships"]["device"]["data"]["id"] != target
        }
        for val in light._device_tool_ids.values():
            assert val not in other_device_tool_ids


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


class TestGetTracks:
    @respx.mock
    def test_returns_list_of_light_tracks(self, f_devices, f_tools, f_playlist_items):
        respx.get(f"{API}/api/devices").mock(return_value=httpx.Response(200, json=f_devices))
        respx.get(f"{API}/api/tools").mock(return_value=httpx.Response(200, json=f_tools))
        respx.get(f"{API}/api/playlists").mock(return_value=httpx.Response(200, json={
            "data": [{"id": "fake-playlist-id", "type": "playlists", "attributes": {}}]
        }))
        respx.get(f"{API}/api/playlist_items").mock(return_value=httpx.Response(200, json=f_playlist_items))

        light = make_light()
        light._fetch_device_tool_ids()
        light._playlist_id = "fake-playlist-id"
        tracks = light.music.get_tracks()

        assert isinstance(tracks, list)
        assert all(isinstance(t, LightTrack) for t in tracks)

    @respx.mock
    def test_tracks_sorted_by_position(self, f_devices, f_tools, f_playlist_items):
        respx.get(f"{API}/api/devices").mock(return_value=httpx.Response(200, json=f_devices))
        respx.get(f"{API}/api/tools").mock(return_value=httpx.Response(200, json=f_tools))
        respx.get(f"{API}/api/playlists").mock(return_value=httpx.Response(200, json={
            "data": [{"id": "fake-playlist-id", "type": "playlists", "attributes": {}}]
        }))
        respx.get(f"{API}/api/playlist_items").mock(return_value=httpx.Response(200, json=f_playlist_items))

        light = make_light()
        light._fetch_device_tool_ids()
        light._playlist_id = "fake-playlist-id"
        tracks = light.music.get_tracks()

        positions = [
            item["attributes"]["position"]
            for item in sorted(f_playlist_items["data"], key=lambda x: x["attributes"]["position"])
        ]
        assert len(tracks) == len(positions)

    @respx.mock
    def test_raises_on_error_response(self, f_devices, f_tools):
        respx.get(f"{API}/api/devices").mock(return_value=httpx.Response(200, json=f_devices))
        respx.get(f"{API}/api/tools").mock(return_value=httpx.Response(200, json=f_tools))
        respx.get(f"{API}/api/playlist_items").mock(return_value=httpx.Response(500, json={}))

        light = make_light()
        light._fetch_device_tool_ids()
        light._playlist_id = "fake-playlist-id"
        with pytest.raises(RuntimeError, match="500"):
            light.music.get_tracks()


def make_note(overrides: dict | None = None) -> LightNote:
    data = dict(id="note-1", file_id="file-1", note_type="text", title="old title", updated_at="2026-01-01T00:00:00")
    if overrides:
        data.update(overrides)
    return LightNote(**data)


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
