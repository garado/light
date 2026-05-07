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


def make_light() -> Light:
    """Return a Light instance with auth bypassed."""
    from open_api_specification_client.client import AuthenticatedClient
    from light_api.music import LightMusic
    from light_api.notes import LightNotes
    from light_api.tools import LightTools
    from light_api.podcast import LightPodcasts
    light = Light(email="test@example.com", password="test")
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
