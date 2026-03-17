
import os
import functools
from mutagen import File
from rich.console import Console
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

console = Console()

BASE_URL = "https://dashboard.thelightphone.com"

class Light:
    """Methods for interfacing with Light devices."""

    def __init__(self,
                 headless=True,
                 email=None, email_file=None,
                 password=None, password_file=None,
                 phone=None, phone_file=None,
                 device_id=None, device_id_file=None):

        self.headless = headless
        self.email: str = email or self._resolve(email_file, "LIGHT_EMAIL")
        self.password: str = password or self._resolve(password_file, "LIGHT_PASSWORD")
        self.phone: str = phone or self._resolve(phone_file, "LIGHT_PHONE_NUMBER")
        self.device_id: str = device_id or self._resolve(device_id_file, "LIGHT_DEVICE_ID")

    def __enter__(self):
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.firefox.launch(headless=self.headless)
        self.page = self._browser.new_context().new_page()
        self.login()
        return self

    def __exit__(self, *_):
        self._browser.close()
        self._playwright.stop()

    @staticmethod
    def _resolve(filepath: str | None, env_key: str) -> str:
        """Determine secret.

        Args:
            filepath:
            env_key:

        Returns:
            Value of secret.
        """
        if filepath:
            try:
                return open(filepath).read().strip()
            except OSError as e:
                console.print(f"[red]Could not read {filepath}: {e}[/red]")
                raise SystemExit(1)
        if value := os.environ.get(env_key):
            return value
        console.print(f"[red]Must provide --{env_key.removeprefix('LIGHT_').lower().replace('_', '-')} or set {env_key}[/red]")
        raise SystemExit(1)

    @staticmethod
    def _format_phone(number: str) -> str:
        """Format phone number to match what appears in the Light dashboard.

        Example: 1234567890 -> +1 123 456 7890 (very Americentric :P)
        """
        digits = ''.join(c for c in number if c.isdigit())[-10:]
        return f"+1 {digits[0:3]} {digits[3:6]} {digits[6:10]}"

    def login(self) -> None:
        """Authenticate into the Light dashboard."""
        self.page.goto(BASE_URL)
        self.page.wait_for_load_state("networkidle")

        if "/login" not in self.page.url:
            return  # credentials are already cached

        self.page.locator('input[name*="email"]').fill(self.email)
        self.page.locator('input[name*="password"]').fill(self.password)

        with self.page.expect_navigation():
            self.page.locator('label:has-text("Log in")').click()
        self.page.wait_for_load_state("networkidle")

        if "/login" in self.page.url:
            console.print("[red]Login failed — check your credentials.[/red]")
            raise SystemExit(1)

    def _nav_to_dash_root(self) -> None:
        """Navigate to the root dashboard menu."""
        self.page.goto(BASE_URL)
        self.page.wait_for_load_state("networkidle")

        if "/login" in self.page.url:
            self.login()

    def _nav_to_music_root(self) -> None:
        """Navigate to the root music menu."""
        self._nav_to_dash_root()
        self.page.locator('a[href="/devices"]').click()
        self.page.locator('li').filter(has_text=self._format_phone(self.phone)).click()
        self.page.locator('li').filter(has_text='Toolbox').click()
        self.page.locator('li').filter(has_text='Music').click()

    def _nav_to_music_edit(self) -> None:
        """Navigate to 'Music->Edit Playlists' tab."""
        self._nav_to_music_root()
        self.page.locator('a:has-text("Edit playlist")').click()
        self.page.locator('.playlist-table-row').first.wait_for()  # ensure page has loaded

    def _nav_to_music_upload(self) -> None:
        """Navigate to 'Music->Add Songs' tab."""
        self._nav_to_music_root()
        self.page.locator('a:has-text("Add songs")').click()

    def delete_tracks(self, titles: list[str]) -> None:
        """Delete tracks from device.

        Args:
            titles: List of track titles (as they appear in the Light Dashboard) to delete
        """
        self._nav_to_music_edit()

        containers = self.page.locator('button.playlist-table-button').locator('xpath=..')

        for title in titles:
            targets = containers.filter(
                        has=self.page.locator(f'a .heading.playlist-table-song:has-text("{title}")')
                      ).all()

            if not targets:
                console.print(f"[yellow]Not found: {title}[/yellow]")
                continue

            for target in targets:
                if title not in target.inner_html():
                    console.print(f"[red]Safety check failed for: {title}[/red]")
                    continue
                with self.page.expect_response(lambda r: r.request.method == 'DELETE'):
                    target.locator('button.playlist-table-button').click()
                    self.page.wait_for_load_state('networkidle')

            console.print(f"[green]Deleted: {title}[/green]")

    def upload_tracks(self, files: list[str], allow_duplicates: bool = False, match_title_by: str = 'metadata') -> None:
        """Upload tracks to device.

        Args:
            files: List of paths to audio files to upload.
            allow_duplicates: False (default) to overwrite existing matching tracks; True otherwise.
        """
        if not allow_duplicates:
            if match_title_by == 'metadata':
                titles = [File(s)['title'][0] for s in files]
            else:
                titles = [os.path.splitext(os.path.basename(s))[0] for s in files]

            self.delete_tracks(titles)

        self._nav_to_music_upload()
        self.page.locator('input[type="file"]').set_input_files(list(files))

        with self.page.expect_response("**/audios"):
            self.page.locator('button:has-text("upload songs")').click()

        self.page.get_by_text("All Uploads complete.").wait_for(timeout=300000) # 5 min


def with_light(f):
    """Decorator to initialize a Light/Playwright context"""
    @functools.wraps(f)
    def wrapper(*args, email=None, password=None, device_id=None, no_headless=False, **kwargs):
        with Light(email_file=email, password_file=password,
                   phone_file=device_id, headless=not no_headless) as light:
            return f(light, *args, **kwargs)
    return wrapper
