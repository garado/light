import time
import rich_click as click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from core import Light, with_light
from music import SortMode
from tui import LightConfig, run_tui

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.STYLE_COMMANDS_TABLE_COLUMN_WIDTH_RATIO = (1, 3)

console = Console()


@click.group()
@click.option("--email", default=None, help="Light account email address.")
@click.option("--email-file", default=None, help="Path to file containing email.")
@click.option("--password", default=None, help="Light account password.")
@click.option("--password-file", default=None, help="Path to file containing password.")
@click.option("--device-id", default=None, help="Path to file containing phone number.")
@click.option(
    "--device-id-file", default=None, help="Path to file containing device ID."
)
@click.option(
    "--no-headless", is_flag=True, help="Show the browser window during authentication."
)
@click.pass_context
def cli(
    ctx,
    email,
    email_file,
    password,
    password_file,
    device_id,
    device_id_file,
    no_headless,
):
    """**Unofficial CLI for the Light Phone.**

    Manage music, podcasts, and notes on your Light Phone device
    from the comfort of your terminal.

    Credentials can be provided via options, files, or environment variables:
    `LIGHT_EMAIL`, `LIGHT_PASSWORD`, `LIGHT_PHONE_NUMBER`.
    """
    ctx.ensure_object(dict)
    ctx.obj.update(
        {
            "email": email,
            "email_file": email_file,
            "password": password,
            "password_file": password_file,
            "device_id": device_id,
            "device_id_file": device_id_file,
            "no_headless": no_headless,
        }
    )


@cli.group()
def music():
    """Manage your music library.

    Upload tracks, delete them, sort your playlist, and update metadata.
    """
    pass


@cli.group()
def podcast():
    """Manage your podcast subscriptions.

    Add podcasts by RSS feed URL and remove ones you no longer want.
    """
    pass


@cli.group()
def notes():
    """Manage your notes.

    List, add, download, and watch for changes to text and audio notes.
    """
    pass


# ── Podcast commands ──────────────────────────────────────────────────────────


@podcast.command()
@with_light
@click.argument("rss_feed_url")
def add(light: Light, rss_feed_url, **kwargs):
    """Subscribe to a podcast by RSS feed URL.

    The server resolves the title and publisher automatically from the feed.

    **Example:**

    `light podcast add https://feeds.simplecast.com/FO6kxYGj`
    """
    with Progress(
        SpinnerColumn(), TextColumn("{task.description}"), console=console
    ) as progress:
        task = progress.add_task("Adding podcast...")
        p = light.podcast.add_podcast(rss_feed_url)
        progress.update(task, description="Done.")
    console.print(f"[green]Added:[/green] {p.title or rss_feed_url}")
    if p.publisher:
        console.print(f"[dim]Publisher:[/dim] {p.publisher}")


@podcast.command()
@with_light
@click.argument("title")
def delete(light: Light, title, **kwargs):
    """Unfollow a podcast by title.

    Uses exact title matching. Run `light podcast list` to see titles.
    """
    with Progress(
        SpinnerColumn(), TextColumn("{task.description}"), console=console
    ) as progress:
        task = progress.add_task("Deleting podcast...")
        light.podcast.delete_podcast_by_title(title)
        progress.update(task, description="Done.")


# ── Music commands ─────────────────────────────────────────────────────────────


@music.command()
@with_light
@click.argument("songs", nargs=-1, required=True)
@click.option(
    "--allow-duplicates",
    is_flag=True,
    help="Skip duplicate checking and always upload.",
)
@click.option(
    "--match-title-by",
    "-m",
    type=click.Choice(["filename", "metadata"]),
    default="metadata",
    show_default=True,
    help="How to match existing tracks when checking for duplicates.",
)
def upload(light: Light, songs, allow_duplicates, match_title_by, **kwargs):
    """Upload one or more audio files to your device.

    Duplicate detection is on by default — existing tracks with a matching
    title will be replaced. Use `--allow-duplicates` to skip this.

    **Example:**

    `light music upload track1.mp3 track2.mp3`
    """
    with Progress(
        SpinnerColumn(), TextColumn("{task.description}"), console=console
    ) as progress:
        task = progress.add_task("Uploading...")
        light.music.upload_tracks(
            list(songs),
            allow_duplicates=allow_duplicates,
            match_title_by=match_title_by,
        )
        progress.update(task, description="Done.")


@music.command()
@with_light
@click.argument("songs", nargs=-1, required=True)
def delete(light: Light, songs, **kwargs):
    """Delete tracks by title.

    Uses exact title matching. Run `light music list` to see track titles.

    **Example:**

    `light music delete "Song Title" "Another Song"`
    """
    with Progress(
        SpinnerColumn(), TextColumn("{task.description}"), console=console
    ) as progress:
        task = progress.add_task("Deleting...")
        light.music.delete_tracks_by_title(list(songs))
        progress.update(task, description="Done.")


@music.command()
@with_light
@click.argument("field", type=click.Choice(["artist", "title", "none"]))
@click.option(
    "--asc",
    "order",
    flag_value="ascending",
    default=True,
    help="Sort ascending (default).",
)
@click.option("--desc", "order", flag_value="descending", help="Sort descending.")
def sort(light: Light, field, order, **kwargs):
    """Sort tracks by artist, title, or reset to manual order.

    `none` resets to the manual ordering you set in the app.

    **Examples:**

    `light music sort artist --desc`

    `light music sort title`

    `light music sort none`
    """
    with Progress(
        SpinnerColumn(), TextColumn("{task.description}"), console=console
    ) as progress:
        task = progress.add_task("Sorting...")

        descending = order == "descending"

        if field == "artist":
            light.music.set_sort_mode(
                SortMode.ARTIST_DESC if descending else SortMode.ARTIST_ASC
            )
        elif field == "title":
            light.music.set_sort_mode(
                SortMode.TITLE_DESC if descending else SortMode.TITLE_ASC
            )
        elif field == "none":
            light.music.set_sort_mode(SortMode.RANK)

        progress.update(task, description="Done.")


@music.command()
@with_light
@click.argument("title")
@click.option("--new-title", default=None, help="New track title.")
@click.option("--artist", default=None, help="New artist name.")
def update(light: Light, title, new_title, artist, **kwargs):
    """Update metadata for a track.

    Matches by exact title. At least one of `--new-title` or `--artist` must be provided.

    **Example:**

    `light music update "Old Title" --new-title "New Title" --artist "Artist"`
    """
    with Progress(
        SpinnerColumn(), TextColumn("{task.description}"), console=console
    ) as progress:
        task = progress.add_task("Updating...")

        tracks = light.music.get_tracks()
        matches = [t for t in tracks if t.title == title]

        if not matches:
            console.print(f"[yellow]No track found with title: {title}[/yellow]")
            return

        for track in matches:
            light.music.update_track_metadata(
                track.audio_id, title=new_title, artist=artist
            )

        progress.update(task, description="Done.")


@music.command()
@with_light
def list(light: Light, **kwargs):
    """List all tracks on your device."""
    tracks = light.music.get_tracks()
    table = Table(show_header=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Title")
    table.add_column("Artist")
    for i, track in enumerate(tracks, 1):
        table.add_row(str(i), track.title, track.artist)
    console.print(table)


# ── Notes commands ─────────────────────────────────────────────────────────────


@notes.command()
@with_light
def list(light: Light, **kwargs):
    """List all notes on your device.

    Shows the first line of text notes and labels audio notes.
    """
    with Progress(
        SpinnerColumn(), TextColumn("{task.description}"), console=console
    ) as progress:
        task = progress.add_task("Fetching notes...")
        all_notes = light.notes.get_notes()
        progress.update(task, description="Done.")
    for i, note in enumerate(all_notes, 1):
        if note.note_type == "audio":
            preview = f"[dim](audio)[/dim] {note.title}"
        elif note.content and note.content.strip():
            preview = note.content.splitlines()[0]
        else:
            preview = "[dim](empty)[/dim]"
        console.print(f"[dim]{i}.[/dim] {preview}")


@notes.command()
@with_light
@click.argument("path")
def download(light: Light, path: str, **kwargs):
    """Download all notes to a directory.

    Text notes are saved as `.txt`, audio notes as `.m4a`.
    If two notes share a title, the timestamp is appended to disambiguate.

    **Example:**

    `light notes download ~/my-notes`
    """
    with Progress(
        SpinnerColumn(), TextColumn("{task.description}"), console=console
    ) as progress:
        task = progress.add_task("Downloading notes...")
        light.notes.download_notes(path)
        progress.update(task, description="Done.")


@notes.command()
@with_light
@click.argument("title")
@click.argument("content", default=None, required=False)
@click.option(
    "--file",
    "-f",
    "content_file",
    default=None,
    type=click.Path(exists=True),
    help="Read note content from a file instead of inline.",
)
def add(
    light: Light, title: str, content: str | None, content_file: str | None, **kwargs
):
    """Create a new text note.

    Provide content inline as an argument, or from a file with `--file`.

    **Examples:**

    `light notes add "Shopping list" "eggs, milk, bread"`

    `light notes add "Meeting notes" --file notes.txt`
    """
    if content is None and content_file is None:
        raise click.UsageError("Provide CONTENT or --file.")
    if content is not None and content_file is not None:
        raise click.UsageError("CONTENT and --file are mutually exclusive.")
    with Progress(
        SpinnerColumn(), TextColumn("{task.description}"), console=console
    ) as progress:
        task = progress.add_task("Adding note...")
        if content_file:
            light.notes.create_text_note(title, content_file, content_is_path=True)
        else:
            light.notes.create_text_note(title, content)
        progress.update(task, description="Done.")


@notes.command()
@with_light
@click.argument("file_id")
def watch(light: Light, file_id: str, **kwargs):
    """Poll a note for changes and print when it's updated.

    Checks every second and prints when `updated_at` changes.
    Useful for watching a note you're actively editing on your phone.

    **Example:**

    `light notes watch 4f1d3063-085b-4738-8ba1-582c5d1cd9ac`
    """
    note = light.notes.get_note_metadata(file_id)
    last_updated_at = note.updated_at

    while True:
        time.sleep(1)
        note = light.notes.get_note_metadata(file_id)
        if note.updated_at != last_updated_at:
            console.print("[green]Change detected![/green]")
            last_updated_at = note.updated_at


# ── TUI ────────────────────────────────────────────────────────────────────────


@cli.command()
@click.option("--email-file", default=None, help="Path to file containing email.")
@click.option("--password-file", default=None, help="Path to file containing password.")
@click.option(
    "--device-id-file", default=None, help="Path to file containing device ID."
)
@click.option(
    "--no-headless", is_flag=True, help="Show the browser window during authentication."
)
def tui(email_file, password_file, device_id_file, no_headless):
    """Launch the interactive terminal UI.

    A full-screen interface for browsing and managing your music library
    with vim-style keybindings.
    """
    run_tui(
        LightConfig(
            email_file=email_file,
            password_file=password_file,
            phone_file=device_id_file,
            headless=not no_headless,
        )
    )


if __name__ == "__main__":
    cli()
