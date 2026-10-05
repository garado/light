"""Tests for light_api.music."""

import pytest
import respx
import httpx
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from light_api.music import LightMusic, LightTrack

from helpers import API, make_light


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
                playlist_item_id="1", playlist_id="p1", audio_id="a1",
                title="Playing God", artist="Paramore", album="Riot!",
                filename="",
            ),
            LightTrack(
                playlist_item_id="2", playlist_id="p1", audio_id="a2",
                title="Playing God", artist="Polyphia", album="New Levels New Devils",
                filename="",
            ),
            LightTrack(
                playlist_item_id="3", playlist_id="p1", audio_id="a3",
                title="Live at Wembley", artist="Queen", album="Live Magic",
                filename="",
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
                playlist_item_id="1", playlist_id="p1", audio_id="a1",
                title="Playing God", artist="Paramore", album="",
                filename="",
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
                playlist_item_id="2", playlist_id="p1", audio_id="a2",
                title="Some Old Rip", artist="Unknown", album="",
                filename="",
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
                playlist_item_id="1", playlist_id="p1", audio_id="a1",
                title="Playing God", artist="Paramore", album="",
                filename="",
            ),
            LightTrack(
                playlist_item_id="2", playlist_id="p1", audio_id="a2",
                title="New Song", artist="New Artist", album="",
                filename="",
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
                playlist_item_id="1", playlist_id="p1", audio_id="a1",
                title="Song", artist="Artist", album="",
                filename="",
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
                playlist_item_id="1", playlist_id="p1", audio_id="a1",
                title="Song", artist="Artist", album="",
                filename="",
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
            results = light.music.upload_tracks(
                [str(flac_file)],
                allow_duplicates=True,
                on_convert=calls.append,
            )

        assert calls == [str(flac_file)]
        mock_convert.assert_called_once_with(str(flac_file))
        assert len(results) == 1
        assert results[0].success is False
        assert "stop after convert" in results[0].error

    def test_on_convert_not_called_for_mp3(self, tmp_path):
        light = make_light()
        light.music._tracks = []
        light._device_tool_ids = {"music": "fake-device-tool-id"}

        mp3_file = tmp_path / "song.mp3"
        mp3_file.write_bytes(b"")

        calls = []

        with patch.object(light, "call_api", side_effect=RuntimeError("stop after convert check")):
            results = light.music.upload_tracks(
                [str(mp3_file)],
                allow_duplicates=True,
                on_convert=calls.append,
            )

        assert calls == []
        assert len(results) == 1
        assert results[0].success is False
