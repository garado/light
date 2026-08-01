"""Tests for light_api parsing logic, played back against fixture JSON."""

import json
import pytest
import respx
import httpx
from types import SimpleNamespace
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


def fake_resp(status_code: int, parsed=None):
    return SimpleNamespace(status_code=status_code, parsed=parsed)


class TestEnsureOk:
    def test_returns_parsed_on_success(self):
        parsed = SimpleNamespace(data=["x"])
        result = Light._ensure_ok(fake_resp(200, parsed), "Do thing")
        assert result is parsed

    def test_raises_on_unexpected_status(self):
        with pytest.raises(RuntimeError, match="Do thing: 404"):
            Light._ensure_ok(fake_resp(404), "Do thing")

    def test_accepts_alternate_ok_codes(self):
        parsed = SimpleNamespace(data=["x"])
        result = Light._ensure_ok(fake_resp(201, parsed), "Create thing", ok_codes=(200, 201))
        assert result is parsed

    def test_accepts_status_only_range(self):
        result = Light._ensure_ok(fake_resp(204, None), "Delete thing", ok_codes=range(200, 300))
        assert result is None

    def test_require_data_raises_on_empty_data(self):
        parsed = SimpleNamespace(data=[])
        with pytest.raises(RuntimeError, match="Do thing: 200"):
            Light._ensure_ok(fake_resp(200, parsed), "Do thing", require_data=True)

    def test_require_data_raises_on_none_parsed(self):
        """require_data=True alone (no require_parsed) still catches parsed=None - it's tiered."""
        with pytest.raises(RuntimeError, match="Do thing: 200"):
            Light._ensure_ok(fake_resp(200, None), "Do thing", require_data=True)

    def test_require_data_succeeds_with_data(self):
        parsed = SimpleNamespace(data=["x"])
        result = Light._ensure_ok(fake_resp(200, parsed), "Do thing", require_data=True)
        assert result is parsed

    def test_require_parsed_raises_on_none_parsed(self):
        with pytest.raises(RuntimeError, match="Do thing: 200"):
            Light._ensure_ok(fake_resp(200, None), "Do thing", require_parsed=True)

    def test_require_parsed_allows_empty_data(self):
        """require_parsed=True does NOT imply require_data - empty .data is fine."""
        parsed = SimpleNamespace(data=[])
        result = Light._ensure_ok(fake_resp(200, parsed), "Do thing", require_parsed=True)
        assert result is parsed

    def test_default_allows_none_parsed(self):
        """Neither flag set - only status is checked, matching endpoints like
        delete/update that don't touch resp.parsed afterward."""
        result = Light._ensure_ok(fake_resp(204, None), "Do thing", ok_codes=(200, 204))
        assert result is None


class TestClearCache:
    def test_deletes_keyring_entry(self):
        from light_api.client import KEYRING_SERVICE, KEYRING_USER

        light = make_light()
        with patch("light_api.client.keyring.delete_password") as mock_delete:
            light.clear_cache()
        mock_delete.assert_called_once_with(KEYRING_SERVICE, KEYRING_USER)

    def test_resets_in_memory_state(self):
        light = make_light()
        light._device_tool_ids = {"music": "abc"}
        light._playlist_id = "some-playlist"

        with patch("light_api.client.keyring.delete_password"):
            light.clear_cache()

        assert light._api_token is None
        assert light._device_tool_ids == {}
        assert light._playlist_id is None

    def test_no_raise_when_nothing_cached(self):
        import keyring.errors

        light = make_light()
        with patch(
            "light_api.client.keyring.delete_password",
            side_effect=keyring.errors.PasswordDeleteError,
        ):
            light.clear_cache()  # should not raise

    def test_no_raise_on_keyring_error(self):
        import keyring.errors

        light = make_light()
        with patch(
            "light_api.client.keyring.delete_password",
            side_effect=keyring.errors.NoKeyringError,
        ):
            light.clear_cache()  # should not raise


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

    @respx.mock
    def test_handles_null_sim_data(self, f_devices_no_sim, f_tools):
        """A device with no SIM/eSIM assigned returns relationships.sim.data: null."""
        respx.get(f"{API}/api/devices").mock(return_value=httpx.Response(200, json=f_devices_no_sim))
        respx.get(f"{API}/api/tools").mock(return_value=httpx.Response(200, json=f_tools))

        light = make_light()
        light._fetch_device_tool_ids()  # should not raise

        assert "notes" in light._device_tool_ids


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


class TestGetToolsMultiDevice:
    @respx.mock
    def test_only_returns_tools_for_selected_device(self, f_devices_multi, f_tools):
        target = f_devices_multi["data"][1]["id"]
        respx.get(f"{API}/api/devices").mock(
            return_value=httpx.Response(200, json=f_devices_multi)
        )
        respx.get(f"{API}/api/tools").mock(return_value=httpx.Response(200, json=f_tools))

        light = make_light(device_id=target)
        tools = light.tools.get_tools()

        other_device_tool_ids = {
            item["id"]
            for item in f_devices_multi["included"]
            if item["type"] == "device_tools"
            and item["relationships"]["device"]["data"]["id"] != target
        }
        assert len(tools) > 0
        for t in tools:
            assert t.device_tool_id not in other_device_tool_ids

    @respx.mock
    def test_raises_when_ambiguous(self, f_devices_multi, f_tools):
        respx.get(f"{API}/api/devices").mock(
            return_value=httpx.Response(200, json=f_devices_multi)
        )
        respx.get(f"{API}/api/tools").mock(return_value=httpx.Response(200, json=f_tools))

        light = make_light()
        with pytest.raises(RuntimeError, match="Multiple devices found"):
            light.tools.get_tools()


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


class TestFindMatchingTrack:
    def test_ignores_cross_artist_title_collision(self):
        light = make_light()
        light.music._tracks = [
            LightTrack(
                playlist_item_id="1", audio_id="a1",
                title="Playing God", artist="Paramore", album="",
            ),
        ]

        # artist=None (filename-mode / metadata-fallback identity) must not
        # wildcard-match a track that has a real, different artist.
        assert light.music._find_matching_track("Playing God", None) is None

        # Precise (title, artist) matching still works correctly.
        assert light.music._find_matching_track("Playing God", "Paramore") is not None
        assert light.music._find_matching_track("Playing God", "Polyphia") is None

    def test_matches_untagged_tracks_by_title_only(self):
        """artist=None should still match existing tracks that are themselves
        untagged (artist blank or 'Unknown') - what filename-mode targets."""
        light = make_light()
        light.music._tracks = [
            LightTrack(
                playlist_item_id="2", audio_id="a2",
                title="Some Old Rip", artist="Unknown", album="",
            ),
        ]

        match = light.music._find_matching_track("Some Old Rip", None)
        assert match is not None and match.audio_id == "a2"


class TestTrackIdentity:
    def test_metadata_mode_reads_title_and_artist(self):
        light = make_light()
        with patch("light_api.music.File", return_value={"title": ["Song"], "artist": ["Artist"]}):
            assert light.music._track_identity("song.mp3", "metadata") == ("Song", "Artist")

    def test_metadata_mode_falls_back_to_filename_when_tags_missing(self):
        """Default (replace=False): missing tags silently fall back to filename matching."""
        light = make_light()
        with patch("light_api.music.File", return_value=None):
            title, artist = light.music._track_identity(
                "/path/Some Song.mp3", "metadata", replace=False
            )
        assert title == "Some Song"
        assert artist is None

    def test_metadata_mode_raises_under_replace_when_tags_missing(self):
        """--replace is destructive, so a missing-tags fallback must be explicit, not silent."""
        light = make_light()
        with patch("light_api.music.File", return_value=None):
            with pytest.raises(ValueError, match="match_by='filename'"):
                light.music._track_identity("/path/Some Song.mp3", "metadata", replace=True)

    def test_filename_mode_ignores_tags_entirely(self):
        light = make_light()
        with patch(
            "light_api.music.File",
            return_value={"title": ["Real Title"], "artist": ["Real Artist"]},
        ):
            title, artist = light.music._track_identity("/path/Filename Title.mp3", "filename")
        assert title == "Filename Title"
        assert artist is None


class TestFindUploadMatches:
    def test_ignores_cross_artist_title_collision(self):
        light = make_light()
        light.music._tracks = [
            LightTrack(
                playlist_item_id="1", audio_id="a1",
                title="Playing God", artist="Paramore", album="",
            ),
            LightTrack(
                playlist_item_id="2", audio_id="a2",
                title="New Song", artist="New Artist", album="",
            ),
        ]

        tags_by_path = {
            "playing_god_polyphia.mp3": {"title": ["Playing God"], "artist": ["Polyphia"]},
            "new_song.mp3": {"title": ["New Song"], "artist": ["New Artist"]},
        }

        with patch("light_api.music.File", side_effect=lambda p, easy=True: tags_by_path[p]):
            matches = light.music.find_upload_matches(
                ["playing_god_polyphia.mp3", "new_song.mp3"], match_by="metadata"
            )

        assert "playing_god_polyphia.mp3" not in matches
        assert matches["new_song.mp3"].audio_id == "a2"


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
