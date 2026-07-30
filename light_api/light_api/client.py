from __future__ import annotations

import httpx
import json
import keyring
import logging
import os

from typing import TYPE_CHECKING, Any, Callable, final

from open_api_specification_client.api.default import get_api_playlists
from open_api_specification_client.client import AuthenticatedClient

if TYPE_CHECKING:
    from light_api.music import LightMusic
    from light_api.podcast import LightPodcasts
    from light_api.notes import LightNotes
    from light_api.tools import LightTools

KEYRING_SERVICE = "unofficial-light-api"
KEYRING_USER = "session"
API_BASE = "https://production.lightphonecloud.com"
API_HEADERS = {"Accept": "application/vnd.api+json"}

log = logging.getLogger(f"light.{__name__}")


@final
class Light:
    """Methods for interfacing with Light devices."""

    def __init__(
        self,
        email: str | None = None,
        email_file: str | None = None,
        password: str | None = None,
        password_file: str | None = None,
        phone: str | None = None,
        phone_file: str | None = None,
        device_id: str | None = None,
        device_id_file: str | None = None,
    ) -> None:
        self.email: str | None = email or self._resolve(email_file, "LIGHT_EMAIL")
        self.password: str | None = password or self._resolve(
            password_file, "LIGHT_PASSWORD"
        )
        self.phone: str | None = phone or self._resolve(
            phone_file, "LIGHT_PHONE_NUMBER"
        )
        self.device_id: str | None = device_id or self._resolve(
            device_id_file, "LIGHT_DEVICE_ID"
        )

        if self.phone and self.device_id:
            raise RuntimeError(
                "phone and device id are mutually exclusive - provide only one"
            )

        self._api_token: str | None = None
        self._api_client: AuthenticatedClient | None = None
        self._device_tool_ids: dict[str, str] = {}
        self._playlist_id: str | None = None

        self.music: LightMusic
        self.podcast: LightPodcasts
        self.notes: LightNotes
        self.tools: LightTools

    def login(self) -> None:
        """Authenticate via the authorizations API and store the bearer token."""
        if self._api_token is not None:
            return

        if not self.email or not self.password:
            raise RuntimeError("No cached session - provide email and password")

        resp = httpx.post(
            f"{API_BASE}/api/authorizations",
            json={"email": self.email, "password": self.password},
            headers={**API_HEADERS, "Content-Type": "application/vnd.api+json"},
            timeout=30,
        )

        if not resp.is_success:
            raise RuntimeError(f"Login failed: {resp.status_code}")

        included = resp.json()["included"][0]
        token = included["attributes"]["token"]

        if token is None:
            raise RuntimeError("Login succeeded but no token found in response")

        self._api_token = token

    def reauth(self) -> None:
        """Re-authenticate and refresh the API client. Called on 401."""
        log.info("Re-authenticating")
        self._api_token = None
        self.login()
        self._save_cache()
        self._api_client = AuthenticatedClient(
            base_url=API_BASE,
            token=self._api_token,
            headers=API_HEADERS,
        )

    def call_api(self, func: Callable[..., Any], **kwargs: Any) -> Any:
        """Call an API function, re-authenticating once on 401."""
        resp = func(**kwargs)
        if resp.status_code == 401:
            self.reauth()
            resp = func(**kwargs)
        return resp

    def __enter__(self) -> Light:
        """Sets up API session."""
        log.info("Authenticating")

        if self._load_cache() and self._validate_cache():
            log.info("Using cached session")
        else:
            self.login()
            self._save_cache()

        self._api_client = AuthenticatedClient(
            base_url=API_BASE,
            token=self._api_token,
            headers=API_HEADERS,
        )

        expected = {"music", "notes", "podcast"}
        if not expected.issubset(self._device_tool_ids) or not self._playlist_id:
            self._fetch_device_tool_ids()
            self._fetch_playlist_id()
            self._save_cache()

        from light_api.music import LightMusic
        from light_api.podcast import LightPodcasts
        from light_api.notes import LightNotes
        from light_api.tools import LightTools

        self.music = LightMusic(self)
        self.podcast = LightPodcasts(self)
        self.notes = LightNotes(self)
        self.tools = LightTools(self)

        log.info("Authentication complete")
        return self

    def __exit__(self, *_: object) -> None:
        pass

    def _load_cache(self) -> bool:
        """Load cached data from keyring."""
        log.debug("Loading cache")

        try:
            raw = keyring.get_password(KEYRING_SERVICE, KEYRING_USER)
        except (keyring.errors.NoKeyringError, keyring.errors.KeyringLocked) as e:
            log.debug(f"Keyring error: {e}")
            return False

        if raw is None:
            log.debug("Keyring: no entry found")
            return False

        try:
            data = json.loads(raw)
            self._api_token = data["api_token"]
            self._device_tool_ids = data["device_tool_ids"]
            self._playlist_id = data["playlist_id"]
            log.debug("Cache loaded successfully")
            return True
        except (KeyError, json.JSONDecodeError) as e:
            log.debug(f"Error: {e}")
            return False

    def _save_cache(self) -> None:
        """Cache data to keyring."""
        try:
            keyring.set_password(
                KEYRING_SERVICE,
                KEYRING_USER,
                json.dumps(
                    {
                        "api_token": self._api_token,
                        "device_tool_ids": self._device_tool_ids,
                        "playlist_id": self._playlist_id,
                    }
                ),
            )
        except (keyring.errors.NoKeyringError, keyring.errors.KeyringLocked) as e:
            log.warning(f"Keyring error: {e}")

    def _validate_cache(self) -> bool:
        """Check if cached auth token is valid."""
        client = AuthenticatedClient(
            base_url=API_BASE,
            token=self._api_token,
            headers=API_HEADERS,
        )
        resp = get_api_playlists.sync_detailed(
            client=client,
            device_tool_id=self._device_tool_ids.get("music"),
        )
        return resp.status_code == 200

    def _fetch_playlist_id(self) -> None:
        music_id = self._device_tool_ids.get("music")
        if not music_id:
            raise RuntimeError("Could not find music device_tool_id in /api/devices")
        resp = get_api_playlists.sync_detailed(
            client=self._api_client,
            device_tool_id=music_id,
        )
        if resp.status_code != 200 or not resp.parsed or not resp.parsed.data:
            raise RuntimeError(f"Could not fetch playlists: {resp.status_code}")
        self._playlist_id = resp.parsed.data[0].id

    def _fetch_device_tool_ids(self) -> None:
        """Populate _device_tool_ids for all installed tools.

        The Light API has two relevant endpoints:
          - GET /api/devices: returns the device record plus "included" items which are
            device_tool records (one per installed tool). Each has a unique `id` (the
            device_tool_id used in subsequent API calls) and a relationship pointing to
            its global tool ID.
          - GET /api/tools?device_id=...: returns the global tool catalog with human-readable
            namespace strings (e.g. "com.light.music", "com.light.notes").

        To get each device tool id, cross-reference the two: build a map of global_tool_id -> namespace
        from /api/tools, then walk the /api/devices included items, look up each item's global tool ID in
        that map, and classify it as "music", "notes", or "podcast" based on the namespace string.
        """
        from open_api_specification_client.api.default import (
            get_api_devices,
            get_api_tools,
        )
        from open_api_specification_client.types import Unset

        devices_resp = get_api_devices.sync_detailed(client=self._api_client)
        if (
            devices_resp.status_code != 200
            or not devices_resp.parsed
            or not devices_resp.parsed.data
        ):
            raise RuntimeError(f"Could not fetch devices: {devices_resp.status_code}")
        device_id = devices_resp.parsed.data[0].id

        tools_resp = get_api_tools.sync_detailed(
            client=self._api_client, device_id=device_id
        )
        if tools_resp.status_code != 200 or not tools_resp.parsed:
            raise RuntimeError(f"Could not fetch tools: {tools_resp.status_code}")

        tool_ns: dict[str, str] = {
            t.id: t.attributes.namespace.lower() for t in tools_resp.parsed.data
        }

        for item in devices_resp.parsed.included:
            if isinstance(item.relationships, Unset) or isinstance(item.relationships.tool, Unset):
                continue
            ns = tool_ns.get(item.relationships.tool.data.id, "")
            if "note" in ns:
                self._device_tool_ids["notes"] = item.id
            elif "podcast" in ns:
                self._device_tool_ids["podcast"] = item.id
            elif "music" in ns or "playlist" in ns:
                self._device_tool_ids["music"] = item.id

    @staticmethod
    def _resolve(filepath: str | None, env_key: str) -> str | None:
        if filepath:
            try:
                with open(filepath) as f:
                    return f.read().strip()
            except OSError as e:
                raise RuntimeError(f"Could not read {filepath}: {e}") from e
        return os.environ.get(env_key)

    @staticmethod
    def _format_phone(number: str) -> str:
        digits: str = "".join(c for c in number if c.isdigit())[-10:]
        return f"+1 {digits[0:3]} {digits[3:6]} {digits[6:10]}"
