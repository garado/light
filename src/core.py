import os
import json
import functools
from typing import TYPE_CHECKING, Any, Callable, final

import keyring
from rich.console import Console
from playwright.sync_api import APIResponse, Browser, Page, Playwright, sync_playwright

console = Console()

BASE_URL = "https://dashboard.thelightphone.com"
KEYRING_SERVICE = "unofficial-light-api"
KEYRING_USER = "session"


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
        self.headless: bool = headless
        self.email: str = email or self._resolve(email_file, "LIGHT_EMAIL")
        self.password: str = password or self._resolve(password_file, "LIGHT_PASSWORD")
        self.phone: str = phone or self._resolve(phone_file, "LIGHT_PHONE_NUMBER")
        self.device_id: str = device_id or self._resolve(
            device_id_file, "LIGHT_DEVICE_ID"
        )
        self._api_token: str | None = None
        self._device_tool_id: str | None = None
        self._playlist_id: str | None = None
        self._podcast_device_tool_id: str | None = None

        self._playwright: Playwright
        self._browser: Browser
        self._page: Page

        # namespaced modules
        self.music: "LightMusic"
        self.podcast: "LightPodcasts"

        if TYPE_CHECKING:
            from music import LightMusic
            from podcast import LightPodcasts

    def __enter__(self) -> "Light":
        """Start Playwright context and grab auth stuff."""
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.firefox.launch(headless=self.headless)
        self._page = self._browser.new_context().new_page()

        console.print("[green]Authenticating...[/green]")

        if self._load_cache() and self._validate_cache():
            console.print("[green]Using cached session.[/green]")
        else:
            self.login()
            self._fetch_device_tool_id()
            self._save_cache()

        from music import LightMusic
        from podcast import LightPodcasts

        self.music = LightMusic(self)
        self.podcast = LightPodcasts(self)

        console.print("[green]Authentication complete.[/green]")

        return self

    def __exit__(self, *_: object) -> None:
        """Stop Playwright context."""
        self._browser.close()
        self._playwright.stop()

    def _request(
        self,
        url: str,
        method: str = "GET",
        data: dict[str, Any] | None = None,
        timeout: int = 30_000,
    ) -> APIResponse:
        """Make an authenticated request to the Light API.

        Args:
            url: URL of API endpoint.
            method: HTTP method.
            data: Request payload.
            timeout: Timeout in milliseconds.
        """
        headers: dict[str, str] = {
            "Authorization": self._api_token or "",
            "Accept": "application/vnd.api+json",
        }

        if data is not None:
            headers["Content-Type"] = "application/vnd.api+json"

        return self._page.request.fetch(
            url,
            method=method,
            headers=headers,
            data=json.dumps(data) if data is not None else None,
            timeout=timeout,
        )

    def _load_cache(self) -> bool:
        try:
            raw = keyring.get_password(KEYRING_SERVICE, KEYRING_USER)
        except keyring.errors.NoKeyringError:
            return False
        if raw is None:
            return False
        try:
            data = json.loads(raw)
            self._api_token = data["api_token"]
            self._device_tool_id = data["device_tool_id"]
            self._playlist_id = data["playlist_id"]
            self._podcast_device_tool_id = data.get("podcast_device_tool_id")
            return True
        except (KeyError, json.JSONDecodeError):
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
                }),
            )
        except keyring.errors.NoKeyringError:
            pass

    def _validate_cache(self) -> bool:
        # dummy api call
        resp = self._request(
            f"https://production.lightphonecloud.com/api/playlists"
            f"?playlist_ids={self._playlist_id}"
            f"&device_tool_id={self._device_tool_id}",
            method="GET",
        )
        return resp.ok

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
    def _resolve(filepath: str | None, env_key: str) -> str:
        """Resolve a secret from a file or environment variable.

        Args:
            filepath: Path to file containing the secret.
            env_key: Environment variable name.

        Returns:
            Value of secret.
        """
        if filepath:
            try:
                with open(filepath) as f:
                    return f.read().strip()
            except OSError as e:
                console.print(f"[red]Could not read {filepath}: {e}[/red]")
                raise SystemExit(1)
        if value := os.environ.get(env_key):
            return value
        console.print(
            f"[red]Must provide --{env_key.removeprefix('LIGHT_').lower().replace('_', '-')} or set {env_key}[/red]"
        )
        raise SystemExit(1)

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

        self._page.goto(BASE_URL)
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
        self._page.goto(BASE_URL)
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

    def _check_response(self, response: APIResponse, context: str = "") -> None:
        if not response.ok:
            raise RuntimeError(f"{context}: {response.status} {response.text()}")


def with_light(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to initialize a Light/Playwright context."""

    @functools.wraps(f)
    def wrapper(
        *args: Any,
        email: str | None = None,
        password: str | None = None,
        device_id: str | None = None,
        no_headless: bool = False,
        **kwargs: Any,
    ) -> Any:
        with Light(
            email_file=email,
            password_file=password,
            phone_file=device_id,
            headless=not no_headless,
        ) as light:
            return f(light, *args, **kwargs)

    return wrapper
