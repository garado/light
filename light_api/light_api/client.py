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
        headless: bool = True,  # kept for backwards compat, unused
    ) -> None:
        self.email: str | None = email or self._resolve(email_file, "LIGHT_EMAIL")
        self.password: str | None = password or self._resolve(password_file, "LIGHT_PASSWORD")
        self.phone: str | None = phone or self._resolve(phone_file, "LIGHT_PHONE_NUMBER")
        self._api_token: str | None = None
        self._api_client: AuthenticatedClient | None = None
        self._device_tool_id: str | None = None
        self._playlist_id: str | None = None
        self._podcast_device_tool_id: str | None = None
        self._notes_device_tool_id: str | None = None

        self.music: LightMusic
        self.podcast: LightPodcasts
        self.notes: LightNotes

    def login(self) -> None:
        """Authenticate via the authorizations API and store the bearer token."""
        if self._api_token is not None:
            return

        if not self.email or not self.password:
            raise RuntimeError("No cached session - provide email and password")

        resp = httpx.post(
            f"{API_BASE}/api/authorizations",
            json={"email": self.email, "password": self.password},
            headers=API_HEADERS,
        )

        if not resp.is_success:
            raise RuntimeError(f"Login failed: {resp.status_code}")

        token = next(
            (i["attributes"]["token"] for i in resp.json()["included"] if i["type"] == "tokens"),
            None,
        )

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

        if not self._device_tool_id or not self._playlist_id:
            self._fetch_device_tool_id()
            self._save_cache()

        from light_api.music import LightMusic
        from light_api.podcast import LightPodcasts
        from light_api.notes import LightNotes

        self.music = LightMusic(self)
        self.podcast = LightPodcasts(self)
        self.notes = LightNotes(self)

        log.info("Authentication complete")
        return self

    def __exit__(self, *_: object) -> None:
        pass

    def _load_cache(self) -> bool:
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
            self._device_tool_id = data["device_tool_id"]
            self._playlist_id = data["playlist_id"]
            self._podcast_device_tool_id = data.get("podcast_device_tool_id")
            self._notes_device_tool_id = data.get("notes_device_tool_id")
            log.debug("Cache loaded successfully")
            return True
        except (KeyError, json.JSONDecodeError) as e:
            log.debug(f"Error: {e}")
            return False

    def _save_cache(self) -> None:
        try:
            keyring.set_password(
                KEYRING_SERVICE,
                KEYRING_USER,
                json.dumps({
                    "api_token": self._api_token,
                    "device_tool_id": self._device_tool_id,
                    "playlist_id": self._playlist_id,
                    "podcast_device_tool_id": self._podcast_device_tool_id,
                    "notes_device_tool_id": self._notes_device_tool_id,
                }),
            )
        except (keyring.errors.NoKeyringError, keyring.errors.KeyringLocked) as e:
            log.warning(f"Keyring error: {e}")

    def _validate_cache(self) -> bool:
        client = AuthenticatedClient(
            base_url=API_BASE,
            token=self._api_token,
            headers=API_HEADERS,
        )
        resp = get_api_playlists.sync_detailed(
            client=client,
            device_tool_id=self._device_tool_id,
        )
        return resp.status_code == 200

    def _fetch_device_tool_id(self) -> None:
        """Fetch music device_tool_id and playlist_id from the playlists API."""
        resp = get_api_playlists.sync_detailed(client=self._api_client)
        if resp.status_code != 200 or not resp.parsed or not resp.parsed.data:
            raise RuntimeError(f"Could not fetch device_tool_id: {resp.status_code}")
        playlist = resp.parsed.data[0]
        self._playlist_id = playlist.id
        self._device_tool_id = playlist.attributes.device_tool_id

    def _fetch_notes_device_tool_id(self) -> None:
        """Fetch notes device_tool_id from the notes API."""
        from open_api_specification_client.api.default import get_api_notes
        resp = get_api_notes.sync_detailed(client=self._api_client)
        if resp.status_code != 200 or not resp.parsed or not resp.parsed.data:
            raise RuntimeError("Could not fetch notes device_tool_id: no notes on device - add a note first")
        self._notes_device_tool_id = resp.parsed.data[0].attributes.device_tool_id

    def _fetch_podcast_device_tool_id(self) -> None:
        """Fetch podcast device_tool_id from the followed podcasts API."""
        from open_api_specification_client.api.default import get_api_followed_podcasts
        resp = get_api_followed_podcasts.sync_detailed(client=self._api_client)
        if resp.status_code != 200 or not resp.parsed or not resp.parsed.data:
            raise RuntimeError("Could not fetch podcast device_tool_id: no podcasts on device - add one first")
        self._podcast_device_tool_id = resp.parsed.data[0].attributes.device_tool_id

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
