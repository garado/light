"""Tests for light_api.client (Light core: auth cache, keyring, device/tool resolution)."""

import pytest
import respx
import httpx
from types import SimpleNamespace
from unittest.mock import patch

from light_api.client import Light

from helpers import API, make_light, fake_resp


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
