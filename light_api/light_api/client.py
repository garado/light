from __future__ import annotations

import json
import keyring
import logging
import os

from typing import TYPE_CHECKING, Any, Callable, final
from urllib.error import URLError
from urllib.request import Request, urlopen

from light_api import endpoints
from open_api_specification_client.api.default import get_api_playlists
from open_api_specification_client.client import AuthenticatedClient

if TYPE_CHECKING:
    from playwright.sync_api import Browser, Page, Playwright

KEYRING_SERVICE = "unofficial-light-api"
KEYRING_USER = "session"
API_BASE = "https://production.lightphonecloud.com"
API_HEADERS = {"Accept": "application/vnd.api+json"}

log = logging.getLogger(f"light.{__name__}")

class _RawResponse:
    """Minimal response wrapper for urllib fetches (used for raw S3 presigned URL calls)."""

    def __init__(self, status: int, content: bytes) -> None:
        self.status = status
        self._content = content

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300

    def body(self) -> bytes:
        return self._content

    def text(self) -> str:
        return self._content.decode()

    def json(self) -> Any:
        return json.loads(self._content)


@final
class Light:
    """Methods for interfacing with Light devices."""

    def __init__(
        self,
        headless: bool = True,
        email: str | None = None,
        email_file: str | None = None,
        password: str | None = None,
        password_file: str | None = None,
        phone: str | None = None,
        phone_file: str | None = None,
    ) -> None:
        # secrets
        self.email: str | None = email or self._resolve(email_file, "LIGHT_EMAIL")
        self.password: str | None = password or self._resolve(
            password_file, "LIGHT_PASSWORD"
        )
        self.phone: str | None = phone or self._resolve(
            phone_file, "LIGHT_PHONE_NUMBER"
        )
        self._api_token: str | None = None  # raw bearer token (no "Bearer " prefix)
        self._api_client: AuthenticatedClient | None = None
        self._device_tool_id: str | None = None
        self._playlist_id: str | None = None
        self._podcast_device_tool_id: str | None = None
        self._notes_device_tool_id: str | None = None

        # if auth with playwright is needed
        self.headless: bool = headless
        self._playwright: Playwright
        self._browser: Browser
        self._page: Page

        # modules
        self.music: LightMusic
        self.podcast: LightPodcasts
        self.notes: LightNotes

        if TYPE_CHECKING:
            from light_api.music import LightMusic
            from light_api.podcast import LightPodcasts
            from light_api.notes import LightNotes

    def reauth(self) -> None:
        """Re-authenticate and refresh the API client. Should be called on a 401."""
        log.info("Re-authenticating")
        self._api_token = None
        self._start_playwright()
        self.login()
        self._save_cache()
        self._api_client = AuthenticatedClient(
            base_url=API_BASE,
            token=self._api_token,
            headers=API_HEADERS,
        )

    def call_api(self, func: "Callable[[], Any]", **kwargs: "Any") -> "Any":
        """Call an API function, re-authenticating once on 401."""
        resp = func(**kwargs)
        if resp.status_code == 401:
            self.reauth()
            resp = func(**kwargs)
        return resp

    def __enter__(self) -> Light:
        """Authenticate, launching Playwright only if the cache is not usable."""
        log.info("Authenticating")

        if self._load_cache() and self._validate_cache():
            log.info("Using cached session")
        else:
            self._start_playwright()
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
        if hasattr(self, "_browser"):
            self._browser.close()
        if hasattr(self, "_playwright"):
            self._playwright.stop()

    def _start_playwright(self) -> None:
        """Launch the browser (idempotent)."""
        if hasattr(self, "_playwright"):
            return
        from playwright.sync_api import sync_playwright
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.firefox.launch(headless=self.headless)
        self._page = self._browser.new_context().new_page()

    def _fetch(
        self,
        url: str,
        method: str = "GET",
        headers: dict[str, str] | None = None,
        data: bytes | str | None = None,
        timeout: int = 30_000,
    ) -> _RawResponse:
        """Make a raw (unauthenticated) request, e.g. to presigned S3 URLs."""
        if isinstance(data, str):
            data = data.encode()
        req = Request(url, method=method, headers=headers or {}, data=data)
        try:
            with urlopen(req, timeout=timeout / 1000) as resp:
                return _RawResponse(resp.status, resp.read())
        except URLError as e:
            code = e.code if hasattr(e, "code") else 0
            return _RawResponse(code, b"")

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
                json.dumps(
                    {
                        "api_token": self._api_token,
                        "device_tool_id": self._device_tool_id,
                        "playlist_id": self._playlist_id,
                        "podcast_device_tool_id": self._podcast_device_tool_id,
                        "notes_device_tool_id": self._notes_device_tool_id,
                    }
                ),
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

    @staticmethod
    def _resolve(filepath: str | None, env_key: str) -> str | None:
        """Resolve a secret from a file or environment variable.

        Returns None if not found — errors are deferred to login() where
        credentials are actually needed (keyring may make them unnecessary).
        """
        if filepath:
            try:
                with open(filepath) as f:
                    return f.read().strip()
            except OSError as e:
                raise RuntimeError(f"Could not read {filepath}: {e}") from e
        return os.environ.get(env_key)

    @staticmethod
    def _format_phone(number: str) -> str:
        """Format phone number to match what appears in the Light dashboard.

        Example: 1234567890 -> +1 123 456 7890 (very Americentric :P)
        """
        digits: str = "".join(c for c in number if c.isdigit())[-10:]
        return f"+1 {digits[0:3]} {digits[3:6]} {digits[6:10]}"

    def login(self) -> None:
        """Authenticate into the Light dashboard and grab auth tokens."""
        if self._api_token is not None:
            return  # auth is already cached

        if not self.email or not self.password:
            raise RuntimeError("No cached session found — provide email, password, and phone number")

        self._start_playwright()
        self._page.goto(endpoints.DASHBOARD)
        self._page.wait_for_load_state("networkidle")

        self._page.locator('input[name*="email"]').fill(self.email)
        self._page.locator('input[name*="password"]').fill(self.password)

        with self._page.expect_response(
            lambda r: "lightphonecloud.com" in r.url
        ) as resp_info:
            with self._page.expect_navigation():
                self._page.locator('label:has-text("Log in")').click()

        self._page.wait_for_load_state("networkidle")

        if "/login" in self._page.url:
            raise RuntimeError("Login failed — check your credentials")

        body: dict[str, Any] = resp_info.value.json()

        token = next(
            (i["attributes"]["token"] for i in body["included"] if i["type"] == "tokens"),
            None,
        )

        if token is None:
            raise RuntimeError("Login succeeded but no token found in response")

        self._api_token = token

    def _nav_to_dash_root(self) -> None:
        """Navigate to the root dashboard menu."""
        self._page.goto(endpoints.DASHBOARD)
        self._page.wait_for_load_state("networkidle")

        if "/login" in self._page.url:
            self.login()

    def _nav_to_music_root(self) -> None:
        """Navigate to the root music menu."""
        self._nav_to_dash_root()
        self._page.locator('a[href="/devices"]').click()
        self._page.locator("li").filter(has_text=self._format_phone(self.phone)).click()
        self._page.locator("li").filter(has_text="Toolbox").click()
        self._page.locator("li").filter(has_text="Music").click()

    def _nav_to_podcasts_root(self) -> None:
        """Navigate to the podcasts tool page."""
        self._nav_to_dash_root()
        self._page.locator('a[href="/devices"]').click()
        self._page.locator("li").filter(has_text=self._format_phone(self.phone)).click()
        self._page.locator("li").filter(has_text="Toolbox").click()
        self._page.locator("li").filter(has_text="Podcasts").click()

    def _nav_to_notes_root(self) -> None:
        """Navigate to the notes tool page."""
        self._nav_to_dash_root()
        self._page.locator('a[href="/devices"]').click()
        self._page.locator("li").filter(has_text=self._format_phone(self.phone)).click()
        self._page.locator("li").filter(has_text="Toolbox").click()
        self._page.locator("li").filter(has_text="Notes").click()
        self._page.locator("li").filter(has_text="View Notes").click()

    def _fetch_notes_device_tool_id(self) -> None:
        """Fetch notes device_tool_id from the notes API."""
        from open_api_specification_client.api.default import get_api_notes
        resp = get_api_notes.sync_detailed(client=self._api_client)
        if resp.status_code != 200 or not resp.parsed or not resp.parsed.data:
            raise RuntimeError("Could not fetch notes device_tool_id: no notes on device — add a note first")
        self._notes_device_tool_id = resp.parsed.data[0].attributes.device_tool_id

    def _fetch_podcast_device_tool_id(self) -> None:
        """Fetch podcast device_tool_id from the followed podcasts API."""
        from open_api_specification_client.api.default import get_api_followed_podcasts
        resp = get_api_followed_podcasts.sync_detailed(client=self._api_client)
        if resp.status_code != 200 or not resp.parsed or not resp.parsed.data:
            raise RuntimeError("Could not fetch podcast device_tool_id: no podcasts on device — add one first")
        self._podcast_device_tool_id = resp.parsed.data[0].attributes.device_tool_id

    def nav_to_music_edit(self) -> None:
        """Navigate to 'Music->Edit Playlists' tab."""
        self._nav_to_music_root()
        self._page.locator('a:has-text("Edit playlist")').click()
        self._page.locator(
            ".playlist-table-row"
        ).first.wait_for()  # ensure page has loaded

    def _check_response(self, response: _RawResponse, context: str = "") -> None:
        if not response.ok:
            raise RuntimeError(f"{context}: {response.status} {response.text()}")


