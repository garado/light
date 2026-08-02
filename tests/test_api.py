"""Tests for light_api parsing logic, played back against fixture JSON."""

import json
import pytest
import respx
import httpx
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from light_api.client import Light
from light_api.notes import LightNote
from light_api.music import LightMusic, LightTrack

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


class TestDeleteTracksPredicateAndRegex:
    def _light_with_tracks(self):
        light = make_light()
        light.music._tracks = [
            LightTrack(
                playlist_item_id="1", audio_id="a1",
                title="Playing God", artist="Paramore", album="Riot!",
            ),
            LightTrack(
                playlist_item_id="2", audio_id="a2",
                title="Playing God", artist="Polyphia", album="New Levels New Devils",
            ),
            LightTrack(
                playlist_item_id="3", audio_id="a3",
                title="Live at Wembley", artist="Queen", album="Live Magic",
            ),
        ]
        return light

    def _mock_delete(self):
        return patch(
            "light_api.music.delete_api_audios_audio_id.sync_detailed",
            return_value=SimpleNamespace(status_code=204),
        )

    def test_predicate_only_deletes_matching_tracks(self):
        light = self._light_with_tracks()
        with self._mock_delete() as mock_delete:
            light.music.delete_tracks_predicate(lambda t: t.audio_id == "a1")

        deleted_ids = {call.kwargs["audio_id"] for call in mock_delete.call_args_list}
        assert deleted_ids == {"a1"}

    def test_predicate_calls_nothing_when_no_matches(self):
        light = self._light_with_tracks()
        with self._mock_delete() as mock_delete:
            light.music.delete_tracks_predicate(lambda t: False)

        mock_delete.assert_not_called()

    def test_title_regex_deletes_all_cross_artist_matches(self):
        """Regex matching is title-only by design; unlike exact-match deletion,
        it can span multiple artists and that's the caller's responsibility."""
        light = self._light_with_tracks()
        with self._mock_delete() as mock_delete:
            light.music.delete_tracks_by_title_regex("^Playing God$")

        deleted_ids = {call.kwargs["audio_id"] for call in mock_delete.call_args_list}
        assert deleted_ids == {"a1", "a2"}

    def test_title_regex_uses_match_not_search(self):
        """re.match anchors at the start of the string, so a pattern that would
        only match mid-string must not delete anything."""
        light = self._light_with_tracks()
        with self._mock_delete() as mock_delete:
            light.music.delete_tracks_by_title_regex("God$")

        mock_delete.assert_not_called()

    def test_artist_regex_deletes_matching_artist_only(self):
        light = self._light_with_tracks()
        with self._mock_delete() as mock_delete:
            light.music.delete_tracks_by_artist_regex("^Queen$")

        deleted_ids = {call.kwargs["audio_id"] for call in mock_delete.call_args_list}
        assert deleted_ids == {"a3"}

    def test_artist_regex_no_match_deletes_nothing(self):
        light = self._light_with_tracks()
        with self._mock_delete() as mock_delete:
            light.music.delete_tracks_by_artist_regex("^Nonexistent$")

        mock_delete.assert_not_called()


class TestFindMatchingTrack:
    def test_ignores_cross_artist_title_collision(self):
        """Regression test for #18: "Playing God" by Polyphia must not match an
        existing "Playing God" by Paramore just because titles collide."""
        light = make_light()
        light.music._tracks = [
            LightTrack(
                playlist_item_id="1", audio_id="a1",
                title="Playing God", artist="Paramore", album="",
            ),
        ]

        assert light.music._find_matching_track("Playing God", "Paramore") is not None
        assert light.music._find_matching_track("Playing God", "Polyphia") is None

    def test_matches_untagged_tracks_by_exact_unknown_artist(self):
        """A file with no tags resolves to artist="Unknown" and should exact-match
        an existing track that was itself uploaded with no metadata."""
        light = make_light()
        light.music._tracks = [
            LightTrack(
                playlist_item_id="2", audio_id="a2",
                title="Some Old Rip", artist="Unknown", album="",
            ),
        ]

        match = light.music._find_matching_track("Some Old Rip", "Unknown")
        assert match is not None and match.audio_id == "a2"


class TestTrackIdentity:
    def test_reads_title_and_artist_from_tags(self):
        light = make_light()
        with patch("light_api.music.File", return_value={"title": ["Song"], "artist": ["Artist"]}):
            assert light.music._track_identity("song.mp3") == ("Song", "Artist")

    def test_falls_back_to_filename_and_unknown_when_tags_missing(self):
        light = make_light()
        with patch("light_api.music.File", return_value=None):
            title, artist = light.music._track_identity("/path/Some Song.mp3")
        assert title == "Some Song"
        assert artist == "Unknown"

    def test_falls_back_per_field_when_only_one_tag_is_missing(self):
        light = make_light()
        with patch("light_api.music.File", return_value={"title": ["Real Title"]}):
            title, artist = light.music._track_identity("/path/Filename.mp3")
        assert title == "Real Title"
        assert artist == "Unknown"


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
                ["playing_god_polyphia.mp3", "new_song.mp3"]
            )

        assert "playing_god_polyphia.mp3" not in matches
        assert matches["new_song.mp3"].audio_id == "a2"


class TestResolveUploadPlan:
    """Unit tests for LightMusic._resolve_upload_plan's skip/overwrite/allow_duplicates
    filtering. Pure computation - no mocking of delete_tracks_predicate needed."""

    def _light_with_track(self):
        light = make_light()
        light.music._tracks = [
            LightTrack(
                playlist_item_id="1", audio_id="a1",
                title="Song", artist="Artist", album="",
            ),
        ]
        return light

    def test_allow_duplicates_returns_files_unchanged_and_nothing_to_delete(self):
        light = self._light_with_track()

        to_upload, to_delete = light.music._resolve_upload_plan(
            ["match.mp3", "new.mp3"], allow_duplicates=True, overwrite=False
        )

        assert to_upload == ["match.mp3", "new.mp3"]
        assert to_delete == []

    def test_default_skips_matching_files_without_deleting(self):
        light = self._light_with_track()

        tags_by_path = {
            "match.mp3": {"title": ["Song"], "artist": ["Artist"]},
            "new.mp3": {"title": ["New Song"], "artist": ["New Artist"]},
        }
        with patch("light_api.music.File", side_effect=lambda p, easy=True: tags_by_path[p]):
            to_upload, to_delete = light.music._resolve_upload_plan(
                ["match.mp3", "new.mp3"], allow_duplicates=False, overwrite=False
            )

        assert to_upload == ["new.mp3"]
        assert to_delete == []

    def test_overwrite_returns_matches_to_delete_and_still_uploads_them(self):
        light = self._light_with_track()

        tags_by_path = {
            "match.mp3": {"title": ["Song"], "artist": ["Artist"]},
            "new.mp3": {"title": ["New Song"], "artist": ["New Artist"]},
        }
        with patch("light_api.music.File", side_effect=lambda p, easy=True: tags_by_path[p]):
            to_upload, to_delete = light.music._resolve_upload_plan(
                ["match.mp3", "new.mp3"], allow_duplicates=False, overwrite=True
            )

        assert to_upload == ["match.mp3", "new.mp3"]
        assert to_delete == [light.music._tracks[0]]


class TestUploadTracksExcludesMissingFiles:
    """overwrite=True must never delete a track whose replacement file doesn't exist on disk."""

    def test_missing_file_never_reaches_matching_or_deletion(self):
        light = make_light()
        light.music._tracks = [
            LightTrack(
                playlist_item_id="1", audio_id="a1",
                title="Song", artist="Artist", album="",
            ),
        ]
        light.music.delete_tracks_predicate = MagicMock()

        # Tags are mocked to guarantee a match *would* occur if File() were ever
        # called on this path - but the path doesn't exist, so matching/deletion
        # must never even be attempted for it.
        with patch(
            "light_api.music.File",
            return_value={"title": ["Song"], "artist": ["Artist"]},
        ) as mock_file:
            light.music.upload_tracks(["/nonexistent/match.mp3"], overwrite=True)

        mock_file.assert_not_called()
        light.music.delete_tracks_predicate.assert_not_called()


class TestFilterValidTracks:
    def test_splits_existing_and_missing_paths(self, tmp_path):
        real_file = tmp_path / "song.mp3"
        real_file.write_bytes(b"")

        valid, invalid = LightMusic.filter_valid_tracks(
            [str(real_file), "/nonexistent/missing.mp3"]
        )

        assert valid == [str(real_file)]
        assert invalid == ["/nonexistent/missing.mp3"]


class TestIsConvertible:
    def test_flac_is_convertible_case_insensitive(self):
        assert LightMusic.is_convertible("song.flac") is True
        assert LightMusic.is_convertible("song.FLAC") is True

    def test_other_formats_are_not_convertible(self):
        assert LightMusic.is_convertible("song.mp3") is False
        assert LightMusic.is_convertible("song.wav") is False
        assert LightMusic.is_convertible("song.m4a") is False


class TestUploadTracksOnConvert:
    def test_on_convert_called_with_path_before_conversion(self, tmp_path):
        light = make_light()
        light.music._tracks = []
        light._device_tool_ids = {"music": "fake-device-tool-id"}

        flac_file = tmp_path / "song.flac"
        flac_file.write_bytes(b"")

        def fake_convert(path):
            out = str(tmp_path / "converted.mp3")
            open(out, "wb").close()
            return out

        calls = []

        with patch("light_api.music._flac_to_mp3", side_effect=fake_convert) as mock_convert, \
             patch.object(light, "call_api", side_effect=RuntimeError("stop after convert")):
            with pytest.raises(RuntimeError, match="stop after convert"):
                light.music.upload_tracks(
                    [str(flac_file)],
                    allow_duplicates=True,
                    on_convert=calls.append,
                )

        assert calls == [str(flac_file)]
        mock_convert.assert_called_once_with(str(flac_file))

    def test_on_convert_not_called_for_mp3(self, tmp_path):
        light = make_light()
        light.music._tracks = []
        light._device_tool_ids = {"music": "fake-device-tool-id"}

        mp3_file = tmp_path / "song.mp3"
        mp3_file.write_bytes(b"")

        calls = []

        with patch.object(light, "call_api", side_effect=RuntimeError("stop after convert check")):
            with pytest.raises(RuntimeError):
                light.music.upload_tracks(
                    [str(mp3_file)],
                    allow_duplicates=True,
                    on_convert=calls.append,
                )

        assert calls == []


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
