import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from core import Light, with_light
from music import SortMode
from tui import LightConfig, run_tui

console = Console()

common_options = [
    click.option("--email", default=None),
    click.option("--email-file", default=None),
    click.option("--password", default=None),
    click.option("--password-file", default=None),
    click.option("--device-id", default=None),
    click.option("--device-id-file", default=None),
    click.option("--no-headless", is_flag=True),
]


def with_common_options(f):
    for option in common_options:
        f = option(f)
    return f


@click.group()
def cli():
    """Interface with Light device."""
    pass


@cli.group()
def music():
    """Manage Light music library."""
    pass


@cli.group()
def podcast():
    """Manage Light podcasts."""
    pass


@podcast.command()
@with_common_options
@with_light
@click.argument("rss_feed_url")
def add(light: Light, rss_feed_url, **kwargs):
    """Subscribe to a podcast by RSS feed URL."""
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
@with_common_options
@with_light
@click.argument("title")
def delete(light: Light, title, **kwargs):
    """Unfollow a podcast by title."""
    with Progress(
        SpinnerColumn(), TextColumn("{task.description}"), console=console
    ) as progress:
        task = progress.add_task("Deleting podcast...")
        light.podcast.delete_podcast_by_title(title)
        progress.update(task, description="Done.")


@music.command()
@with_common_options
@with_light
@click.argument("songs", nargs=-1, required=True)
@click.option("--allow-duplicates", is_flag=True)
@click.option(
    "--match-title-by",
    "-m",
    type=click.Choice(["filename", "metadata"]),
    default="metadata",
)
def upload(light: Light, songs, allow_duplicates, match_title_by, **kwargs):
    """Upload audio files to device."""
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
@with_common_options
@with_light
@click.argument("songs", nargs=-1, required=True)
def delete(light: Light, songs, **kwargs):
    """Delete tracks by title."""
    with Progress(
        SpinnerColumn(), TextColumn("{task.description}"), console=console
    ) as progress:
        task = progress.add_task("Deleting...")
        light.music.delete_tracks_by_title(list(songs))
        progress.update(task, description="Done.")


@music.command()
@with_common_options
@with_light
@click.argument("field", type=click.Choice(["artist", "title", "none"]))
@click.option("--asc", "order", flag_value="ascending", default=True)
@click.option("--desc", "order", flag_value="descending", help="Sort descending")
def sort(light: Light, field, order, **kwargs):
    """Sort tracks by artist, title, or reset to manual order."""
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
@with_common_options
@with_light
@click.argument("title")
@click.option("--new-title", default=None, help="New track title")
@click.option("--artist", default=None, help="New artist name")
def update(light: Light, title, new_title, artist, **kwargs):
    """Update metadata for a track matching TITLE."""
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
@with_common_options
@with_light
def list(light: Light, **kwargs):
    """List all tracks on device."""
    tracks = light.music.get_tracks()
    table = Table(show_header=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Title")
    table.add_column("Artist")
    for i, track in enumerate(tracks, 1):
        table.add_row(str(i), track.title, track.artist)
    console.print(table)


@cli.group()
def notes():
    """Manage Light notes."""
    pass


@notes.command()
@with_common_options
@with_light
def list(light: Light, **kwargs):
    """List all notes on device."""
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
@with_common_options
@with_light
@click.argument("path")
def download(light: Light, path: str, **kwargs):
    """Download all notes to file."""
    with Progress(
        SpinnerColumn(), TextColumn("{task.description}"), console=console
    ) as progress:
        task = progress.add_task("Downloading notes...")
        light.notes.download_notes(path)
        progress.update(task, description="Done.")


@cli.command()
@click.option("--email-file", default=None)
@click.option("--password-file", default=None)
@click.option("--device-id-file", default=None)
@click.option("--no-headless", is_flag=True)
def tui(email_file, password_file, device_id_file, no_headless):
    """Launch the interactive TUI."""
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
