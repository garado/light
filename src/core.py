from __future__ import annotations
import logging

import click
import endpoints
import functools
import json
import keyring
import os
from rich.console import Console
from typing import TYPE_CHECKING, Any, Callable, final
from urllib.error import URLError
from urllib.request import Request, urlopen

if TYPE_CHECKING:
    from playwright.sync_api import Browser, Page, Playwright

KEYRING_SERVICE = "unofficial-light-api"
KEYRING_USER = "session"

console = Console()
log = logging.getLogger(f"light.{__name__}")

class _RawResponse:
    """Minimal response wrapper for urllib fetches, mimicking the Playwright APIResponse interface."""

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
        device_id: str | None = None,
        device_id_file: str | None = None,
    ) -> None:
        # secrets
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
        self._api_token: str | None = None
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
            from music import LightMusic
            from podcast import LightPodcasts
            from notes import LightNotes

    def __enter__(self) -> Light:
        """Authenticate, launching Playwright only if the cache is not usable."""
        console.print("[green]Authenticating...[/green]")

        if self._load_cache() and self._validate_cache():
            console.print("[green]Using cached session.[/green]")
        else:
            self._start_playwright()
            self.login()
            self._fetch_device_tool_id()
            self._save_cache()

        from music import LightMusic
        from podcast import LightPodcasts
        from notes import LightNotes

        self.music = LightMusic(self)
        self.podcast = LightPodcasts(self)
        self.notes = LightNotes(self)

        console.print("[green]Authentication complete.[/green]")

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

    def _request(
        self,
        url: str,
        method: str = "GET",
        data: dict[str, Any] | None = None,
        timeout: int = 30_000,
    ) -> _RawResponse:
        """Make an authenticated request to the Light API."""
        headers: dict[str, str] = {
            "Authorization": self._api_token or "",
            "Accept": "application/vnd.api+json",
        }
        body: bytes | None = None
        if data is not None:
            headers["Content-Type"] = "application/vnd.api+json"
            body = json.dumps(data).encode()

        req = Request(url, method=method, headers=headers, data=body)
        try:
            with urlopen(req, timeout=timeout / 1000) as resp:
                return _RawResponse(resp.status, resp.read())
        except URLError as e:
            code = e.code if hasattr(e, "code") else 0
            body_bytes = e.read() if hasattr(e, "read") else b""
            return _RawResponse(code, body_bytes)

    def _load_cache(self) -> bool:
        log.debug("loading cache")

        try:
            raw = keyring.get_password(KEYRING_SERVICE, KEYRING_USER)
        except (keyring.errors.NoKeyringError, keyring.errors.KeyringLocked) as e:
            log.debug(f"keyring error: {e}")
            return False
        if raw is None:
            log.debug(f"keyring: no entry found {e}")
            return False
        try:
            data = json.loads(raw)
            self._api_token = data["api_token"]
            self._device_tool_id = data["device_tool_id"]
            self._playlist_id = data["playlist_id"]
            self._podcast_device_tool_id = data.get("podcast_device_tool_id")
            self._notes_device_tool_id = data.get("notes_device_tool_id")
            log.debug("cache loaded successfully")
            return True
        except (KeyError, json.JSONDecodeError) as e:
            log.debug(f"error: {e}")
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
        except (keyring.errors.NoKeyringError, keyring.errors.KeyringLocked):
            print("keyring error")
            pass

    def _validate_cache(self) -> bool:
        url = endpoints.playlists(self._playlist_id, self._device_tool_id)
        req = Request(
            url,
            headers={
                "Authorization": self._api_token or "",
                "Accept": "application/vnd.api+json",
            },
        )
        try:
            with urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except URLError:
            return False

    def _fetch_device_tool_id(self) -> None:
        """Navigate to music edit page once to grab dynamic config values.

        TODO Not sure what device_tool_id actually does.
        """
        with self._page.expect_response(
            lambda r: "/api/playlists" in r.url and r.request.method == "GET"
        ) as playlists_resp:
            with self._page.expect_response(
                lambda r: "playlist_items" in r.url and r.request.method == "GET"
            ):
                self.nav_to_music_edit()

        self._device_tool_id = playlists_resp.value.url.split("device_tool_id=")[
            1
        ].split("&")[0]
        playlists_body: dict[str, Any] = playlists_resp.value.json()
        data: dict[str, Any] | list[dict[str, Any]] = playlists_body["data"]
        self._playlist_id = (data if isinstance(data, dict) else data[0])["id"]

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
                console.print(f"[red]Could not read {filepath}: {e}[/red]")
                raise SystemExit(1)
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
            console.print(
                "[red]No cached session found. Provide --email and --password (or set LIGHT_EMAIL / LIGHT_PASSWORD).[/red]"
            )
            raise SystemExit(1)

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
            console.print("[red]Login failed — check your credentials.[/red]")
            raise SystemExit(1)

        body: dict[str, Any] = resp_info.value.json()
        token: str = next(
            i["attributes"]["token"] for i in body["included"] if i["type"] == "tokens"
        )
        self._api_token = f"Bearer {token}"

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
        """Navigate to notes page to capture the notes device_tool_id."""
        with self._page.expect_response(
            lambda r: "/api/notes" in r.url and r.request.method == "GET"
        ) as resp:
            self._nav_to_notes_root()

        url = resp.value.url
        self._notes_device_tool_id = url.split("device_tool_id=")[1].split("&")[0]

    def _fetch_podcast_device_tool_id(self) -> None:
        """Navigate to podcasts page to capture the podcast device_tool_id."""
        with self._page.expect_response(
            lambda r: "/api/followed_podcasts" in r.url and r.request.method == "GET"
        ) as resp:
            self._nav_to_podcasts_root()

        url = resp.value.url
        self._podcast_device_tool_id = url.split("device_tool_id=")[1].split("&")[0]

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


def with_light(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to initialize a Light/Playwright context."""

    @functools.wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        obj = click.get_current_context().find_object(dict) or {}
        try:
            with Light(
                email=obj.get("email"),
                email_file=obj.get("email_file"),
                password=obj.get("password"),
                password_file=obj.get("password_file"),
                phone=obj.get("device_id"),
                phone_file=obj.get("device_id_file"),
                headless=not obj.get("no_headless", False),
            ) as light:
                return f(light, *args, **kwargs)
        except RuntimeError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise SystemExit(1)

    return wrapper
