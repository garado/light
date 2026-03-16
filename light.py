import os
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

console = Console()

BASE_URL = "https://dashboard.thelightphone.com"


def resolve(filepath: str | None, env_key: str) -> str:
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


def format_phone(number: str) -> str:
    """Format phone number to match what appears in the Light dashboard.

    Example: 1234567890 -> +1 123 456 7890 (very Americentric :P)
    """
    digits = ''.join(c for c in number if c.isdigit())[-10:]
    return f"+1 {digits[0:3]} {digits[3:6]} {digits[6:10]}"


def login(page, email: str, password: str) -> None:
    page.goto(f"{BASE_URL}/login")
    page.locator('input[name*="email"]').fill(email)
    page.locator('input[name*="password"]').fill(password)
    page.locator('label:has-text("Log in")').click()
    page.wait_for_url(f"{BASE_URL}/**", wait_until="networkidle")

    if "/login" in page.url:
        console.print("[red]Login failed — check your credentials.[/red]")
        raise SystemExit(1)


def navigate_to_music(page, phone: str) -> None:
    page.locator('a[href="/devices"]').click()
    page.locator('li').filter(has_text=format_phone(phone)).click()
    page.locator('li').filter(has_text='Toolbox').click()
    page.locator('li').filter(has_text='Music').click()


def make_page(playwright, headless: bool):
    browser = playwright.firefox.launch(headless=headless)
    return browser, browser.new_context().new_page()


def delete_titles(page, titles: list[str]) -> None:
    page.locator('a:has-text("Edit playlist")').click()
    page.locator('.playlist-table-row').first.wait_for()
    containers = page.locator('button.playlist-table-button').locator('xpath=..')

    for title in titles:
        targets = containers.filter(
            has=page.locator(f'a .heading.playlist-table-song:has-text("{title}")')
        ).all()

        if not targets:
            console.print(f"[yellow]Not found: {title}[/yellow]")
            continue

        for target in targets:
            if title not in target.inner_html():
                console.print(f"[red]Safety check failed for: {title}[/red]")
                continue
            with page.expect_response(lambda r: r.request.method == 'DELETE'):
                target.locator('button.playlist-table-button').click()
                page.wait_for_load_state('networkidle')
        console.print(f"[green]Deleted: {title}[/green]")


common_options = [
    click.option('--email', default=None, help='File containing email (fallback: LIGHT_EMAIL)'),
    click.option('--password', default=None, help='File containing password (fallback: LIGHT_PASSWORD)'),
    click.option('--device-id', default=None, help='File containing device ID (fallback: LIGHT_DEVICE_ID)'),
    click.option('--no-headless', is_flag=True, help='Show the browser window'),
]

def with_common_options(f):
    for option in reversed(common_options):
        f = option(f)
    return f


@click.group()
def cli():
    """Manage music on your Light Phone."""
    pass


@cli.command()
@with_common_options
@click.argument('songs', nargs=-1, required=True)
@click.option('--no-overwrite', is_flag=True, help='Skip removing existing tracks before upload')
def upload(songs, no_overwrite, email, password, device_id, no_headless):
    """Upload songs to Light Phone."""
    _email = resolve(email, "LIGHT_EMAIL")
    _password = resolve(password, "LIGHT_PASSWORD")
    _device_id = resolve(device_id, "LIGHT_DEVICE_ID")

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        with sync_playwright() as playwright:
            browser, page = make_page(playwright, not no_headless)
            try:
                task = progress.add_task("Logging in...")
                login(page, _email, _password)
                navigate_to_music(page, _device_id)

                if not no_overwrite:
                    titles = [os.path.splitext(os.path.basename(s))[0] for s in songs]
                    progress.update(task, description="Removing existing tracks...")
                    delete_titles(page, titles)
                    page.locator('a:has-text("Music")').click()

                progress.update(task, description=f"Uploading {len(songs)} song(s)...")
                page.locator('a:has-text("Add songs")').click()
                page.locator('input[type="file"]').set_input_files(list(songs))

                with page.expect_response("**/audios"):
                    page.locator('button:has-text("upload songs")').click()

                page.get_by_text("All Uploads complete.").wait_for()
                progress.update(task, description="Done.")
            except PlaywrightTimeoutError as e:
                console.print(f"[red]Timed out: {e}[/red]")
                raise SystemExit(1)
            finally:
                browser.close()

    console.print(f"[green]Uploaded {len(songs)} song(s). It may take some time to process.[/green]")


@cli.command()
@with_common_options
@click.argument('titles', nargs=-1, required=True)
def delete(titles, email, password, device_id, no_headless):
    """Delete specific songs by title."""
    _email = resolve(email, "LIGHT_EMAIL")
    _password = resolve(password, "LIGHT_PASSWORD")
    _device_id = resolve(device_id, "LIGHT_DEVICE_ID")

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        with sync_playwright() as playwright:
            browser, page = make_page(playwright, not no_headless)
            try:
                task = progress.add_task("Logging in...")
                login(page, _email, _password)
                navigate_to_music(page, _device_id)
                delete_titles(page, list(titles))
            except PlaywrightTimeoutError as e:
                console.print(f"[red]Timed out: {e}[/red]")
                raise SystemExit(1)
            finally:
                browser.close()


@cli.command()
@with_common_options
@click.option('-y', '--yes', is_flag=True, help='Skip confirmation')
def clear(email, password, device_id, no_headless, yes):
    """Delete all songs from your Light Phone."""
    if not yes:
        click.confirm("Delete all songs?", abort=True)

    _email = resolve(email, "LIGHT_EMAIL")
    _password = resolve(password, "LIGHT_PASSWORD")
    _device_id = resolve(device_id, "LIGHT_DEVICE_ID")

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        with sync_playwright() as playwright:
            browser, page = make_page(playwright, not no_headless)
            try:
                task = progress.add_task("Logging in...")
                login(page, _email, _password)
                navigate_to_music(page, _device_id)
                page.locator('.playlist-table-row').first.wait_for()

                progress.update(task, description="Clearing songs...")
                while True:
                    buttons = page.locator('button.playlist-table-button')
                    if buttons.count() == 0:
                        break
                    buttons.first.click()
                    page.wait_for_load_state("networkidle")

                progress.update(task, description="Done.")
            except PlaywrightTimeoutError as e:
                console.print(f"[red]Timed out: {e}[/red]")
                raise SystemExit(1)
            finally:
                browser.close()

    console.print("[green]Cleared all songs.[/green]")


if __name__ == "__main__":
    cli()
