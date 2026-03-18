import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from core import Light, with_light
from music import SortMode

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
            light.music.update_track_metadata(track.audio_id, title=new_title, artist=artist)

        progress.update(task, description="Done.")


if __name__ == "__main__":
    cli()
