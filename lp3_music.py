import os
import sys
from typing import Annotated

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

console = Console()
app = typer.Typer(help="Manage music on your Light Phone.")

BASE_URL = "https://dashboard.thelightphone.com"

EmailOpt = Annotated[str | None, typer.Option(help="File containing email (fallback: LIGHT_EMAIL)")]
PasswordOpt = Annotated[str | None, typer.Option(help="File containing password (fallback: LIGHT_PASSWORD)")]
DeviceOpt = Annotated[str | None, typer.Option("--device-id", help="File containing device ID (fallback: LIGHT_DEVICE_ID)")]
HeadlessOpt = Annotated[bool, typer.Option("--no-headless", help="Show the browser window during operation")]


def resolve(filepath: str | None, env_key: str) -> str:
    """Extract secret from either filepath or environment var."""
    if filepath:
        try:
            return open(filepath).read().strip()
        except OSError as e:
            console.print(f"[red]Could not read {filepath}: {e}[/red]")
            raise typer.Exit(1)
    if value := os.environ.get(env_key):
        return value
    console.print(f"[red]Must provide --{env_key.removeprefix('LIGHT_').lower().replace('_', '-')} or set {env_key}[/red]")
    raise typer.Exit(1)


def format_phone(number: str) -> str:
    """Format phone number to match what appears in the Light dashboard.

    Example: 1234567890 -> +1 123 456 7890 (very Americentric :P)
    """
    digits= ''.join(c for c in number if c.isdigit())[-10:]
    return f"+1 {digits[0:3]} {digits[3:6]} {digits[6:10]}"


def login(page, email: str, password: str) -> None:
    page.goto(f"{BASE_URL}/login")
    page.locator('input[name*="email"]').fill(email)
    page.locator('input[name*="password"]').fill(password)
    page.locator('label:has-text("Log in")').click()
    page.wait_for_url(f"{BASE_URL}/**", wait_until="networkidle")

    if "/login" in page.url:
        console.print("[red]Login failed — check your credentials.[/red]")
        raise typer.Exit(1)


def navigate_to_music(page, phone: str) -> None:
    """Navigate to Music menu from the main Light dashboard page."""
    page.locator('a[href="/devices"]').click()
    page.locator('li').filter(has_text=format_phone(phone)).click()
    page.locator('li').filter(has_text='Toolbox').click()
    page.locator('li').filter(has_text='Music').click()


def make_page(playwright, headless: bool):
    browser = playwright.firefox.launch(headless=headless)
    return browser, browser.new_context().new_page()


@app.command()
def upload(
    songs: Annotated[list[str], typer.Argument(help="Audio file(s) to upload")],
    email: EmailOpt = None,
    password: PasswordOpt = None,
    device_id: DeviceOpt = None,
    no_headless: HeadlessOpt = False,
):
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

                progress.update(task, description=f"Uploading {len(songs)} song(s)...")
                navigate_to_music(page, _device_id)
                page.locator('a:has-text("Add songs")').click()
                page.locator('input[type="file"]').set_input_files(songs)

                with page.expect_response("**/audios"):
                    page.locator('button:has-text("upload songs")').click()

                page.get_by_text("All Uploads complete.").wait_for()

                progress.update(task, description="Done.")
            except PlaywrightTimeoutError as e:
                console.print(f"[red]Timed out: {e}[/red]")
                raise typer.Exit(1)
            finally:
                browser.close()

    console.print(f"[green]Uploaded {len(songs)} song(s). It may take some time to process.[/green]")


@app.command()
def delete(
    titles: Annotated[list[str], typer.Argument(help="Song title(s) to delete")],
    email: EmailOpt = None,
    password: PasswordOpt = None,
    device_id: DeviceOpt = None,
    no_headless: HeadlessOpt = False,
):
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
                page.locator('a:has-text("Edit playlist")').click()
                page.locator('.playlist-table-row').first.wait_for()

                containers = page.locator('button.playlist-table-button').locator('xpath=..')

                for title in titles:
                    progress.update(task, description=f"Deleting [bold]{title}[/bold]...")
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
            except PlaywrightTimeoutError as e:
                console.print(f"[red]Timed out: {e}[/red]")
                raise typer.Exit(1)
            finally:
                browser.close()


@app.command()
def clear(
    email: EmailOpt = None,
    password: PasswordOpt = None,
    device_id: DeviceOpt = None,
    no_headless: HeadlessOpt = False,
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Skip confirmation")] = False,
):
    """Delete all songs from your Light Phone."""
    if not yes:
        typer.confirm("Delete all songs?", abort=True)

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
                raise typer.Exit(1)
            finally:
                browser.close()

    console.print("[green]Cleared all songs.[/green]")


if __name__ == "__main__":
    app()
