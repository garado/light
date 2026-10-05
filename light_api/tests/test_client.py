"""Tests for light_api.client (Light core: auth cache, keyring, device/tool resolution)."""

import pytest
import respx
import httpx
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from light_api.client import Light

from helpers import API, make_light, fake_resp


def make_bare_light(**kwargs) -> Light:
    """A Light instance with nothing bypassed - no token, no api client, no modules.

    Unlike make_light(), this is for testing methods (login, __enter__, the lazy
    module properties, etc.) that run their real setup logic.
    """
    return Light(email="test@example.com", password="test", **kwargs)


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
            light.clear_auth_cache()
        mock_delete.assert_called_once_with(KEYRING_SERVICE, KEYRING_USER)

    def test_resets_in_memory_state(self):
        light = make_light()
        light._device_tool_ids = {"music": "abc"}
        light._playlist_id = "some-playlist"

        with patch("light_api.client.keyring.delete_password"):
            light.clear_auth_cache()

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
            light.clear_auth_cache()  # should not raise

    def test_no_raise_on_keyring_error(self):
        import keyring.errors

        light = make_light()
        with patch(
            "light_api.client.keyring.delete_password",
            side_effect=keyring.errors.NoKeyringError,
        ):
            light.clear_auth_cache()  # should not raise


class TestKeyringTimeout:
    """A stuck keyring backend must not hang the program forever, and should be treated
    the same as a normal keyring error."""

    def test_load_auth_cache_returns_false_on_hang(self, monkeypatch):
        import time
        import light_api.client as client_mod

        monkeypatch.setattr(client_mod, "KEYRING_TIMEOUT_SECONDS", 0.2)

        def hang(*args, **kwargs):
            time.sleep(10)

        light = make_light()
        with patch("light_api.client.keyring.get_password", side_effect=hang):
            start = time.monotonic()
            result = light._load_auth_cache()
            elapsed = time.monotonic() - start

        assert result is False
        assert elapsed < 1, "did not time out promptly"

    def test_save_auth_cache_does_not_raise_on_hang(self, monkeypatch):
        import time
        import light_api.client as client_mod

        monkeypatch.setattr(client_mod, "KEYRING_TIMEOUT_SECONDS", 0.2)

        def hang(*args, **kwargs):
            time.sleep(10)

        light = make_light()
        with patch("light_api.client.keyring.set_password", side_effect=hang):
            start = time.monotonic()
            light._save_auth_cache()  # should not raise or hang
            elapsed = time.monotonic() - start

        assert elapsed < 1, "did not time out promptly"

    def test_clear_auth_cache_does_not_raise_on_hang(self, monkeypatch):
        import time
        import light_api.client as client_mod

        monkeypatch.setattr(client_mod, "KEYRING_TIMEOUT_SECONDS", 0.2)

        def hang(*args, **kwargs):
            time.sleep(10)

        light = make_light()
        with patch("light_api.client.keyring.delete_password", side_effect=hang):
            start = time.monotonic()
            light.clear_auth_cache()  # should not raise or hang
            elapsed = time.monotonic() - start

        assert elapsed < 1, "did not time out promptly"

    def test_stuck_thread_does_not_block_process_exit(self, monkeypatch):
        """The worker thread must be daemonized so a call that never returns can't
        keep the interpreter alive."""
        import time
        import light_api.client as client_mod

        monkeypatch.setattr(client_mod, "KEYRING_TIMEOUT_SECONDS", 0.2)

        def hang(*args, **kwargs):
            time.sleep(10)

        thread = None
        orig_thread_cls = client_mod.threading.Thread

        def capture_thread(*args, **kwargs):
            nonlocal thread
            thread = orig_thread_cls(*args, **kwargs)
            return thread

        monkeypatch.setattr(client_mod.threading, "Thread", capture_thread)

        with pytest.raises(client_mod._KeyringTimeout):
            client_mod._call_keyring(hang)

        assert thread is not None
        assert thread.daemon is True


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


class TestInit:
    def test_phone_and_device_id_are_mutually_exclusive(self):
        with pytest.raises(RuntimeError, match="mutually exclusive"):
            Light(email="a@b.com", password="x", phone="555", device_id="dev-1")


class TestResolve:
    def test_reads_from_file_when_given(self, tmp_path):
        f = tmp_path / "email.txt"
        f.write_text("a@b.com\n")
        assert Light._resolve(str(f), "LIGHT_EMAIL") == "a@b.com"

    def test_raises_runtime_error_on_unreadable_file(self):
        with pytest.raises(RuntimeError, match="Could not read"):
            Light._resolve("/nonexistent/path/email.txt", "LIGHT_EMAIL")

    def test_falls_back_to_env_when_no_filepath(self, monkeypatch):
        monkeypatch.setenv("LIGHT_EMAIL", "env@b.com")
        assert Light._resolve(None, "LIGHT_EMAIL") == "env@b.com"

    def test_returns_none_when_neither_filepath_nor_env(self, monkeypatch):
        monkeypatch.delenv("LIGHT_EMAIL", raising=False)
        assert Light._resolve(None, "LIGHT_EMAIL") is None


class TestFormatPhone:
    def test_formats_as_plus1_grouped(self):
        assert Light._format_phone("5125550199") == "+1 512 555 0199"

    def test_strips_non_digits_first(self):
        assert Light._format_phone("(512) 555-0199") == "+1 512 555 0199"


class TestLogin:
    def test_returns_immediately_if_already_authenticated(self):
        light = make_bare_light()
        light._api_token = "already-set"
        light.login()  # should not raise or make any HTTP call
        assert light._api_token == "already-set"

    def test_prompts_for_password_when_missing_and_prompt_given(self):
        light = make_bare_light()
        light.password = None
        light._password_prompt = lambda: "prompted-password"

        @respx.mock
        def run():
            respx.post(f"{API}/api/authorizations").mock(
                return_value=httpx.Response(200, json={
                    "included": [{"attributes": {"token": "tok"}}]
                })
            )
            light.login()

        run()
        assert light.password == "prompted-password"
        assert light._api_token == "tok"

    def test_raises_when_no_credentials_available(self):
        light = make_bare_light()
        light.email = None
        light.password = None
        with pytest.raises(RuntimeError, match="No cached session"):
            light.login()

    @respx.mock
    def test_raises_on_failed_response(self):
        light = make_bare_light()
        respx.post(f"{API}/api/authorizations").mock(return_value=httpx.Response(401, json={}))
        with pytest.raises(RuntimeError, match="Login failed: 401"):
            light.login()

    @respx.mock
    def test_raises_when_token_missing_in_response(self):
        light = make_bare_light()
        respx.post(f"{API}/api/authorizations").mock(
            return_value=httpx.Response(200, json={
                "included": [{"attributes": {"token": None}}]
            })
        )
        with pytest.raises(RuntimeError, match="no token found"):
            light.login()

    @respx.mock
    def test_sets_api_token_on_success(self):
        light = make_bare_light()
        respx.post(f"{API}/api/authorizations").mock(
            return_value=httpx.Response(200, json={
                "included": [{"attributes": {"token": "fresh-token"}}]
            })
        )
        light.login()
        assert light._api_token == "fresh-token"


class TestReauth:
    @respx.mock
    def test_logs_in_again_and_rebuilds_api_client(self):
        light = make_bare_light()
        light._api_token = "stale-token"
        respx.post(f"{API}/api/authorizations").mock(
            return_value=httpx.Response(200, json={
                "included": [{"attributes": {"token": "new-token"}}]
            })
        )
        with patch.object(light, "_save_auth_cache") as mock_save:
            light.reauth()

        assert light._api_token == "new-token"
        assert light._api_client is not None
        mock_save.assert_called_once()


class TestCallApi:
    def test_returns_response_unchanged_when_not_401(self):
        light = make_light()
        func = MagicMock(return_value=fake_resp(200))
        result = light.call_api(func)
        assert result.status_code == 200
        func.assert_called_once()

    def test_reauths_and_retries_once_on_401(self):
        light = make_light()
        func = MagicMock(side_effect=[fake_resp(401), fake_resp(200)])
        with patch.object(light, "reauth") as mock_reauth:
            result = light.call_api(func)

        mock_reauth.assert_called_once()
        assert result.status_code == 200
        assert func.call_count == 2


class TestEnter:
    def _light_with_mocked_collaborators(self, **overrides):
        light = make_bare_light()
        defaults = dict(
            _load_auth_cache=MagicMock(return_value=False),
            _validated_recently=MagicMock(return_value=False),
            _validate_auth_cache=MagicMock(return_value=False),
            login=MagicMock(),
            _save_auth_cache=MagicMock(),
            _fetch_device_tool_ids=MagicMock(),
        )
        defaults.update(overrides)
        for name, mock in defaults.items():
            setattr(light, name, mock)
        return light, defaults

    def test_uses_recent_cache_without_revalidating(self):
        light, mocks = self._light_with_mocked_collaborators(
            _load_auth_cache=MagicMock(return_value=True),
            _validated_recently=MagicMock(return_value=True),
        )
        light._device_tool_ids = {"notes": "x"}  # already populated

        light.__enter__()

        mocks["login"].assert_not_called()
        mocks["_validate_auth_cache"].assert_not_called()
        mocks["_fetch_device_tool_ids"].assert_not_called()

    def test_revalidates_stale_cache_via_api(self):
        light, mocks = self._light_with_mocked_collaborators(
            _load_auth_cache=MagicMock(return_value=True),
            _validated_recently=MagicMock(return_value=False),
            _validate_auth_cache=MagicMock(return_value=True),
        )
        light._device_tool_ids = {"notes": "x"}

        light.__enter__()

        mocks["login"].assert_not_called()
        mocks["_validate_auth_cache"].assert_called_once()
        assert light._validated_at is not None
        mocks["_save_auth_cache"].assert_called_once()

    def test_falls_back_to_login_when_no_cache(self):
        light, mocks = self._light_with_mocked_collaborators(
            _load_auth_cache=MagicMock(return_value=False),
        )
        light._device_tool_ids = {"notes": "x"}

        light.__enter__()

        mocks["login"].assert_called_once()

    def test_falls_back_to_login_when_cache_fails_validation(self):
        light, mocks = self._light_with_mocked_collaborators(
            _load_auth_cache=MagicMock(return_value=True),
            _validated_recently=MagicMock(return_value=False),
            _validate_auth_cache=MagicMock(return_value=False),
        )
        light._device_tool_ids = {"notes": "x"}

        light.__enter__()

        mocks["login"].assert_called_once()

    def test_fetches_device_tool_ids_when_empty(self):
        light, mocks = self._light_with_mocked_collaborators(
            _load_auth_cache=MagicMock(return_value=True),
            _validated_recently=MagicMock(return_value=True),
        )
        light._device_tool_ids = {}

        light.__enter__()

        mocks["_fetch_device_tool_ids"].assert_called_once()

    def test_returns_self(self):
        light, _ = self._light_with_mocked_collaborators(
            _load_auth_cache=MagicMock(return_value=True),
            _validated_recently=MagicMock(return_value=True),
        )
        light._device_tool_ids = {"notes": "x"}
        assert light.__enter__() is light


class TestExit:
    def test_is_a_no_op(self):
        light = make_light()
        assert light.__exit__(None, None, None) is None


class TestLazyProperties:
    def test_notes_property_is_memoized(self):
        light = make_bare_light()
        light._api_client = object()
        from light_api.notes import LightNotes

        first = light.notes
        assert isinstance(first, LightNotes)
        assert light.notes is first

    def test_podcast_property_is_memoized(self):
        light = make_bare_light()
        light._api_client = object()
        from light_api.podcast import LightPodcasts

        first = light.podcast
        assert isinstance(first, LightPodcasts)
        assert light.podcast is first

    def test_contacts_property_is_memoized(self):
        light = make_bare_light()
        light._api_client = object()
        from light_api.contacts import LightContacts

        first = light.contacts
        assert isinstance(first, LightContacts)
        assert light.contacts is first

    def test_devices_property_is_memoized(self):
        light = make_bare_light()
        light._api_client = object()
        from light_api.devices import LightDevices

        first = light.devices
        assert isinstance(first, LightDevices)
        assert light.devices is first

    def test_tools_property_is_memoized(self):
        light = make_bare_light()
        light._api_client = object()
        from light_api.tools import LightTools

        first = light.tools
        assert isinstance(first, LightTools)
        assert light.tools is first

    def test_music_property_fetches_playlist_id_then_memoizes(self):
        light = make_bare_light()
        light._api_client = object()
        light._device_tool_ids = {"music": "music-dtid"}
        from light_api.music import LightMusic

        with patch.object(light, "_fetch_playlist_id") as mock_fetch:
            def fake_fetch():
                light._playlist_id = "pl-1"
            mock_fetch.side_effect = fake_fetch

            first = light.music

        assert isinstance(first, LightMusic)
        mock_fetch.assert_called_once()
        assert light.music is first  # memoized, no second fetch


class TestLoadAuthCache:
    def test_returns_false_when_nothing_cached(self):
        light = make_bare_light()
        with patch("light_api.client.keyring.get_password", return_value=None):
            assert light._load_auth_cache() is False

    def test_populates_fields_and_returns_true_on_valid_entry(self):
        import json

        light = make_bare_light()
        raw = json.dumps({
            "api_token": "tok",
            "device_tool_ids": {"notes": "n1"},
            "playlist_id": "pl-1",
            "validated_at": 123.0,
        })
        with patch("light_api.client.keyring.get_password", return_value=raw):
            assert light._load_auth_cache() is True

        assert light._api_token == "tok"
        assert light._device_tool_ids == {"notes": "n1"}
        assert light._playlist_id == "pl-1"
        assert light._validated_at == 123.0

    def test_returns_false_on_malformed_json(self):
        light = make_bare_light()
        with patch("light_api.client.keyring.get_password", return_value="not json"):
            assert light._load_auth_cache() is False

    def test_returns_false_on_missing_key(self):
        import json

        light = make_bare_light()
        raw = json.dumps({"api_token": "tok"})  # missing device_tool_ids etc.
        with patch("light_api.client.keyring.get_password", return_value=raw):
            assert light._load_auth_cache() is False

    def test_returns_false_on_keyring_error(self):
        import keyring.errors

        light = make_bare_light()
        with patch(
            "light_api.client.keyring.get_password",
            side_effect=keyring.errors.NoKeyringError,
        ):
            assert light._load_auth_cache() is False


class TestValidatedRecently:
    def test_false_when_never_validated(self):
        light = make_light()
        light._validated_at = None
        assert light._validated_recently() is False

    def test_true_within_ttl(self):
        import time

        light = make_light()
        light._validated_at = time.time()
        assert light._validated_recently() is True

    def test_false_after_ttl(self, monkeypatch):
        import time
        import light_api.client as client_mod

        light = make_light()
        light._validated_at = time.time()
        monkeypatch.setattr(
            client_mod.time, "time",
            lambda: light._validated_at + client_mod.AUTH_VALIDATION_TTL_SECONDS + 1,
        )
        assert light._validated_recently() is False


class TestValidateAuthCache:
    def test_true_on_200(self):
        light = make_light()
        light._api_token = "tok"
        with patch(
            "light_api.client.get_api_users_current.sync_detailed",
            return_value=fake_resp(200),
        ):
            assert light._validate_auth_cache() is True

    def test_false_on_non_200(self):
        light = make_light()
        light._api_token = "tok"
        with patch(
            "light_api.client.get_api_users_current.sync_detailed",
            return_value=fake_resp(401),
        ):
            assert light._validate_auth_cache() is False


class TestFetchPlaylistId:
    def test_raises_when_no_music_device_tool_id(self):
        light = make_light()
        light._device_tool_ids = {}
        with pytest.raises(RuntimeError, match="Could not find music device_tool_id"):
            light._fetch_playlist_id()

    def test_sets_playlist_id_from_first_playlist(self):
        light = make_light()
        light._device_tool_ids = {"music": "music-dtid"}
        parsed = SimpleNamespace(data=[SimpleNamespace(id="pl-1")])
        with patch(
            "light_api.client.get_api_playlists.sync_detailed",
            return_value=fake_resp(200, parsed),
        ):
            light._fetch_playlist_id()
        assert light._playlist_id == "pl-1"


class TestCurrentDeviceId:
    def test_resolves_and_memoizes(self, f_devices):
        light = make_light()
        with patch.object(light, "call_api", return_value=fake_resp(200, SimpleNamespace(
            data=[SimpleNamespace(id="dev-1")],
        ))) as mock_call_api:
            first = light.current_device_id
            second = light.current_device_id

        assert first == "dev-1"
        assert second == "dev-1"
        mock_call_api.assert_called_once()  # memoized after first resolution
