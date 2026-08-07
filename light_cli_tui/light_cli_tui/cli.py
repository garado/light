"""
█░░ █ █▀▀ █░█ ▀█▀   █▀▀ █░░ █   ▄█▄   ▀█▀ █░█ █
█▄▄ █ █▄█ █▀█ ░█░   █▄▄ █▄▄ █   ░▀░   ░█░ █▄█ █

Command line tools for Light devices.
"""

import json
import logging
import os
import re
import rich_click as click
from rich.console import Console
from rich.progress import Progress, TaskID, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

from light_api.client import Light
from light_api.music import SortMode
from light_api.tools import ToolName
from light_api import with_light
from light_cli_tui.interactive import (
    confirm_selection_with_repick,
    fuzzy_pick_best,
    fuzzy_pick_interactive,
)
from light_cli_tui.output import render, render_error


click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.STYLE_COMMANDS_TABLE_COLUMN_WIDTH_RATIO = (1, 3)

console = Console()
log = logging.getLogger(f"light.{__name__}")


class JsonAwareGroup(click.RichGroup):
    """Wrapper for command execution adding JSON output support for failures."""

    def invoke(self, ctx: click.Context):
        try:
            return super().invoke(ctx)
        except click.ClickException as e:
            if (ctx.obj or {}).get("json"):
                render_error(e.format_message())
                ctx.exit(e.exit_code)
            raise


@click.group(
    cls=JsonAwareGroup, context_settings={"help_option_names": ["-h", "--help"]}
)
@click.version_option(package_name="light-phone-cli-tui", prog_name="light")
@click.option("--email", default=None, help="Light account email address.")
@click.option("--email-file", default=None, help="Path to file containing email.")
@click.option("--password", default=None, help="Light account password.")
@click.option("--password-file", default=None, help="Path to file containing password.")
@click.option("--phone-number", default=None, help="Phone number.")
@click.option(
    "--phone-number-file", default=None, help="Path to file containing phone number."
)
@click.option(
    "--device-id",
    default=None,
    help="Device UUID to operate on. Mutually exclusive with --phone-number.",
)
@click.option(
    "--device-id-file", default=None, help="Path to file containing device UUID."
)
@click.option(
    "--log-level",
    default="WARNING",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    help="Log level.",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    default=False,
    help="Output machine-readable JSON instead of human-readable text.",
)
@click.pass_context
def cli(
    ctx,
    email,
    email_file,
    password,
    password_file,
    phone_number,
    phone_number_file,
    device_id,
    device_id_file,
    log_level,
    json_output,
):
    """**Unofficial CLI for the Light Phone.**

    Manages music, podcasts, notes, and more on your Light device from the terminal.

    Credentials can be provided via options, files, or environment variables
    (`LIGHT_EMAIL`, `LIGHT_PASSWORD`, `LIGHT_PHONE_NUMBER`, `LIGHT_DEVICE_ID`).

    On accounts with multiple devices, select one via `--phone-number` or
    `--device-id` (mutually exclusive).
    """
    if (phone_number or phone_number_file) and (device_id or device_id_file):
        raise click.UsageError("--phone-number and --device-id are mutually exclusive.")

    logging.basicConfig(format="%(name)s %(levelname)s %(message)s")
    logging.getLogger("light").setLevel(log_level.upper())

    ctx.ensure_object(dict)
    ctx.obj.update(
        {
            "email": email,
            "email_file": email_file,
            "password": password,
            "password_file": password_file,
            "phone_number": phone_number,
            "phone_number_file": phone_number_file,
            "device_id": device_id,
            "device_id_file": device_id_file,
            "json": json_output,
        }
    )


@cli.group()
def music():
    """Music library management.

    Upload tracks, delete them, sort your playlist, and update metadata.
    """
    pass


@cli.group()
def podcasts():
    """Podcast management.

    Add podcasts by RSS feed URL and remove ones you no longer want.
    """
    pass


@cli.group()
def notes():
    """Notes management.

    List, add, and download text and audio notes.
    """
    pass


@cli.group()
def devices():
    """Device introspection.

    Shows device id, phone number, SKU, and serial number.
    """
    pass


# -- Podcast commands ----------------------------------------------------------


@podcasts.command("add")
@with_light
@click.argument("rss_feed_url")
def podcasts_add(light: Light, rss_feed_url):
    """Subscribe to a podcast by RSS feed URL.

    The server resolves the title and publisher automatically from the feed.

    **Example:**

    `light podcasts add https://feeds.simplecast.com/FO6kxYGj`
    """
    p = light.podcast.add_podcast(rss_feed_url)
    console.print(f"[green]Added:[/green] {p.title or rss_feed_url}")
    if p.publisher:
        console.print(f"[dim]Publisher:[/dim] {p.publisher}")


@podcasts.command("list")
@with_light
def podcasts_list(light: Light):
    """List all followed podcasts on your device."""
    podcasts = light.podcast.get_podcasts()

    def render_human_readable():
        if not podcasts:
            console.print("[dim]No podcasts followed.[/dim]")
            return

        table = Table(show_header=True)
        table.add_column("#", style="dim", width=4)
        table.add_column("Title")
        table.add_column("Publisher")

        for i, p in enumerate(podcasts, 1):
            table.add_row(str(i), p.title, p.publisher)

        console.print(table)

    render(podcasts, render_human_readable)


@podcasts.command("delete")
@with_light
@click.argument("title")
def podcasts_delete(light: Light, title):
    """Unfollow a podcast by title.

    Uses exact title matching. Run `light podcasts list` to see titles.
    """
    podcasts = light.podcast.get_podcasts()
    matches = [p for p in podcasts if p.title == title]

    if not matches:
        console.print(f"[yellow]No podcast found with title: {title}[/yellow]")
        return

    for p in matches:
        console.print(f"  {p.title}")
    if not click.confirm("Unfollow?"):
        return

    light.podcast.delete_podcast_by_title(title)


# -- Music commands -------------------------------------------------------------

_VERBOSE_LIST_THRESHOLD = 20


def _filter_tracks_by_regex(tracks, title_regex, artist_regex, album_regex):
    """Keep tracks whose title/artist/album all match their given regex pattern."""
    try:
        title_pattern = re.compile(title_regex) if title_regex else None
        artist_pattern = re.compile(artist_regex) if artist_regex else None
        album_pattern = re.compile(album_regex) if album_regex else None
    except re.error as e:
        raise click.UsageError(f"Invalid regex: {e}")

    return [
        t
        for t in tracks
        if (title_pattern is None or title_pattern.match(t.title))
        and (artist_pattern is None or artist_pattern.match(t.artist))
        and (album_pattern is None or album_pattern.match(t.album))
    ]


@music.command("upload")
@with_light
@click.argument("songs", nargs=-1, required=True)
@click.option(
    "--allow-duplicates",
    is_flag=True,
    help="Allow uploading duplicate tracks.",
)
@click.option(
    "--overwrite",
    is_flag=True,
    help="Overwrite existing matching tracks.",
)
@click.option(
    "--no-convert",
    is_flag=True,
    default=False,
    help="Skip pre-converting non-MP3 files. Light's servers do not correctly set "
    "metadata on non-MP3 files when uploading; pre-converting to MP3 prevents "
    "that from happening.",
    )
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Show the full list of affected tracks.",
)
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    default=False,
    help="When SONGS includes a directory, also walk its subdirectories for audio files.",
)
def music_upload(
    light: Light, songs, allow_duplicates, overwrite, no_convert, verbose, recursive
):
    """Upload audio files (or directories of them) to your device.

    **Examples:**

    `light music upload track1.mp3 track2.mp3`

    `light music upload ~/Music --recursive`
    """
    if overwrite and allow_duplicates:
        raise click.UsageError(
            "--overwrite and --allow-duplicates are mutually exclusive."
        )

    expanded = light.music.expand_music_paths(list(songs), recursive)
    files, invalid_files = light.music.filter_valid_tracks(expanded)
    for file_path in invalid_files:
        console.print(f"[yellow]File not found, skipping: {file_path}[/yellow]")

    if not files:
        console.print("[yellow]No audio files found.[/yellow]")
        return

    matches = light.music.find_upload_matches(files)

    skip_count = len(matches) if matches and not overwrite and not allow_duplicates else 0
    upload_count = len(files) - skip_count

    console.print(f"{upload_count} track{'s' if upload_count != 1 else ''} will be uploaded")
    if matches:
        if skip_count:
            console.print(
                f"{skip_count} existing track{'s' if skip_count != 1 else ''} will be skipped:"
            )
        else:
            verb = "duplicated" if allow_duplicates else "overwritten"
            console.print(
                f"{len(matches)} of these already exist and will be {verb}:"
            )

        if not verbose and len(matches) > _VERBOSE_LIST_THRESHOLD:
            console.print("[dim]Use --verbose/-v to show full list.[/dim]")
        else:
            for file_path, t in matches.items():
                console.print(f"  {file_path} -> {t.artist} — {t.title}")

    to_upload_files = [f for f in files if f not in matches] if skip_count else files
    convert_files = [
        f for f in to_upload_files if not no_convert and light.music.is_convertible(f)
    ]
    if convert_files:
        console.print(
            f"{len(convert_files)} FLAC file{'s' if len(convert_files) != 1 else ''} "
            "will be pre-converted to MP3:"
        )
        if not verbose and len(convert_files) > _VERBOSE_LIST_THRESHOLD:
            console.print("[dim]Use --verbose/-v to show full list.[/dim]")
        else:
            for file_path in convert_files:
                base = os.path.splitext(os.path.basename(file_path))[0]
                console.print(f"  {os.path.basename(file_path)} -> {base}.mp3")

    if not click.confirm("Proceed?"):
        return

    console.print()

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task_id: TaskID | None = None
        current_file: str | None = None
        batch_position = ""

        def on_file_start(index: int, total: int, file_path: str) -> None:
            nonlocal batch_position
            batch_position = f"[{index}/{total}] "

        def on_progress(filename: str, sent: int, total: int) -> None:
            nonlocal task_id, current_file
            if filename != current_file:
                if task_id is not None:
                    progress.remove_task(task_id)
                current_file = filename
                task_id = progress.add_task(f"{batch_position}uploading {filename}", total=100)
            progress.update(task_id, completed=int(sent / total * 100))

        def on_convert(file_path: str) -> None:
            filename = os.path.basename(file_path)
            mp3_name = os.path.splitext(filename)[0] + ".mp3"
            console.print(f"[dim]{batch_position}Converting {filename} -> {mp3_name}[/dim]")

        light.music.upload_tracks(
            files,
            allow_duplicates=allow_duplicates,
            overwrite=overwrite,
            convert_flac=not no_convert,
            on_progress=on_progress,
            on_convert=on_convert,
            on_file_start=on_file_start,
        )


@music.command("delete-all")
@with_light
def music_delete_all(light: Light):
    """Delete ALL tracks on device."""
    if not click.confirm("This will delete ALL tracks on the device. Proceed?"):
        return

    if input('Type "yes i am sure" to confirm: ') != "yes i am sure":
        return

    light.music.delete_all_tracks()


@music.command("delete")
@with_light
@click.argument("songs", nargs=-1)
@click.option(
    "--title", "-t", "title_regex", help="Delete tracks whose title matches this regex pattern."
)
@click.option(
    "--artist", "-a", "artist_regex", help="Delete tracks whose artist matches this regex pattern."
)
@click.option(
    "--album", "-b", "album_regex", help="Delete tracks whose album matches this regex pattern."
)
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    default=False,
    help="Immediately open interactive deletion menu."
)
def music_delete(
    light: Light,
    songs: tuple[str, ...],
    title_regex: str | None,
    artist_regex: str | None,
    album_regex: str | None,
    interactive: bool,
):
    """Delete tracks by fuzzy search, or by regex pattern.

    Each SONGS argument is fuzzy-matched against every track's title, artist,
    and album. By default, the top-scoring match(es) per query are auto-selected
    (ties may select multiple); pass --interactive to pick matches by hand instead.

    If more than one of --title, --artist, --album regex patterns are given, tracks must match all of them.

    **Examples:**

    `light music delete "Playing God"`

    `light music delete -i "Playing God"`

    `light music delete --title '^Live '`

    `light music delete --artist '^The '`

    `light music delete --album '(Deluxe|Remastered)'`
    """
    songs = tuple(s for s in songs if s.strip())
    regex_given = title_regex or artist_regex or album_regex

    if songs and regex_given:
        raise click.UsageError(
            "Provide either song titles or --title/--artist/--album, not both."
        )

    if not songs and not regex_given:
        raise click.UsageError("Provide song titles, or one of --title/--artist/--album.")

    tracks = light.music.get_tracks()

    def repick():
        return fuzzy_pick_interactive(
            songs,
            tracks,
            fields=lambda t: (t.title, t.artist, t.album),
            label=lambda t: f"{t.artist} — {t.album} — {t.title}",
            id_key=lambda t: t.audio_id,
            console=console,
        )

    if regex_given:
        to_delete = _filter_tracks_by_regex(tracks, title_regex, artist_regex, album_regex)
    else:
        if interactive:
            selected = repick()
        else:
            selected = fuzzy_pick_best(
                songs,
                tracks,
                fields=lambda t: (t.title, t.artist, t.album),
                id_key=lambda t: t.audio_id,
                console=console,
            )
        if selected is None:
            console.print("[yellow]Aborted.[/yellow]")
            return
        to_delete = list(selected.values())

    if not to_delete:
        console.print("[yellow]No matching tracks.[/yellow]")
        return

    if regex_given:
        console.print(f"Tracks to delete ({len(to_delete)}):")
        for t in to_delete:
            console.print(f"  {t.artist} — {t.title}")
        if not click.confirm("Proceed?"):
            return
    else:
        result = confirm_selection_with_repick(
            {t.audio_id: t for t in to_delete},
            label=lambda t: f"{t.artist} — {t.album} - {t.title}",
            header="Tracks to delete",
            repick=repick,
            console=console,
        )
        if result is None:
            return
        to_delete = result

    audio_ids = {t.audio_id for t in to_delete}
    light.music.delete_tracks_predicate(lambda t: t.audio_id in audio_ids)


@music.command("sort")
@with_light
@click.argument("field", type=click.Choice(["artist", "title", "artist-album", "none"]))
@click.option(
    "--asc",
    "order",
    flag_value="ascending",
    default=True,
    help="Sort ascending (default).",
)
@click.option("--desc", "order", flag_value="descending", help="Sort descending.")
def music_sort(light: Light, field, order):
    """Sort tracks by artist, title, or reset to manual order.

    `none` resets to the manual ordering you set in the app.

    **Examples:**

    `light music sort artist --desc`

    `light music sort title`

    `light music sort none`
    """
    descending = order == "descending"

    if field == "artist":
        light.music.set_sort_mode(
            SortMode.ARTIST_DESC if descending else SortMode.ARTIST_ASC
        )
    elif field == "title":
        light.music.set_sort_mode(
            SortMode.TITLE_DESC if descending else SortMode.TITLE_ASC
        )
    elif field == "artist-album":
        light.music.set_sort_mode(
            SortMode.ARTIST_ALBUM_DESC if descending else SortMode.ARTIST_ALBUM_ASC
        )
    elif field == "none":
        light.music.set_sort_mode(SortMode.RANK)


@music.command("update")
@with_light
@click.argument("title")
@click.option("--new-title", default=None, help="New track title.")
@click.option("--new-artist", default=None, help="New artist name.")
@click.option("--new-album", default=None, help="New album name.")
def music_update(light: Light, title, new_title, new_artist, new_album):
    """Update metadata for a track.

    Matches by exact title. At least one of `--new-title`, `--new-artist`, or `--new-album` must be provided.

    **Example:**

    `light music update "Old Title" --new-title "New Title" --new-artist "Artist" --new-album "Album"`
    """
    tracks = light.music.get_tracks()
    matches = [t for t in tracks if t.title == title]

    if not matches:
        console.print(f"[yellow]No track found with title: {title}[/yellow]")
        return

    for track in matches:
        light.music.update_track_metadata(
            track.audio_id, title=new_title, artist=new_artist, album=new_album
        )


@music.command("list")
@with_light
def music_list(light: Light):
    """List all tracks on your device."""
    tracks = light.music.get_tracks()

    def render_human_readable():
        table = Table(show_header=True)
        table.add_column("#", style="dim", width=4)
        table.add_column("Title")
        table.add_column("Artist")
        table.add_column("Album")

        for i, track in enumerate(tracks, 1):
            table.add_row(str(i), track.title, track.artist, track.album)

        console.print(table)

    render(tracks, render_human_readable)


# -- Notes commands -------------------------------------------------------------


@notes.command("list")
@with_light
@click.option(
    "--id",
    "-i",
    "show_id",
    default=False,
    type=bool,
    is_flag=True,
    help="Include note ID in output (use with `notes watch`).",
)
@click.option(
    "--content-preview",
    "-c",
    default=False,
    type=bool,
    is_flag=True,
    help="Include content preview in output.",
)
def notes_list(light: Light, show_id=False, content_preview=False):
    """List all notes on your device.

    Shows the first line of text notes and labels audio notes.
    """
    all_notes = light.notes.get_notes()

    def render_human_readable():
        if content_preview:
            console.print(
                f"[dim]Content preview enabled. This might take a while.[/dim]"
            )

        table = Table(show_header=True)
        table.add_column("#", style="dim", width=4)
        if show_id:
            table.add_column("ID")
        table.add_column("Title")
        table.add_column("Type")
        table.add_column("Updated At")
        if content_preview:
            table.add_column("Preview")

        for i, note in enumerate(all_notes, 1):
            row = [str(i)]
            if show_id:
                row.append(note.id)
            row.append(note.title or "[dim](untitled)[/dim]")
            row.append(note.note_type)
            row.append(note.updated_at)

            if content_preview:
                if note.note_type == "audio":
                    preview = "[dim](audio)[/dim]"
                else:
                    content = light.notes.get_note_content(note)
                    if content and content.strip():
                        preview = content.splitlines()[0]
                    else:
                        preview = "[dim](empty)[/dim]"
                row.append(preview)

            table.add_row(*row)

        console.print(table)

    render(all_notes, render_human_readable)


@notes.command("download")
@with_light
@click.argument("path")
def notes_download(light: Light, path: str):
    """Download all notes to a directory.

    Text notes are saved as `.txt`, audio notes as `.m4a`.
    If two notes share a title, the timestamp is appended to disambiguate.

    **Example:**

    `light notes download ~/my-notes`
    """
    light.notes.download_notes(path)


@notes.command("add")
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
def notes_add(light: Light, title: str, content: str | None, content_file: str | None):
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

    if content_file:
        light.notes.create_text_note(title, content_file, content_is_path=True)
    else:
        light.notes.create_text_note(title, content)


# -- Tools commands ------------------------------------------------------------


@cli.group()
def tools():
    """Installed tools introspection."""
    pass


@tools.command("list")
@with_light
def tools_list(light: Light):
    """List all tools installed on your device."""
    all_tools = light.tools.get_tools()

    def render_human_readable():
        table = Table(show_header=True)
        table.add_column("Title")

        for t in all_tools:
            table.add_row(t.title)

        console.print(table)

    render(all_tools, render_human_readable)


@tools.command("add")
@with_light
@click.argument(
    "name", type=click.Choice([t.value for t in ToolName], case_sensitive=False)
)
def tools_add(light: Light, name: str):
    """Install a tool on your device."""
    tool = light.tools.add_tool(name)
    console.print(f"[green]Installed:[/green] {tool.title}")


@tools.command("remove")
@with_light
@click.argument(
    "name", type=click.Choice([t.value for t in ToolName], case_sensitive=False)
)
def tools_remove(light: Light, name: str):
    """Uninstall a tool from your device."""
    if not click.confirm(f"Remove {name}?"):
        return
    light.tools.remove_tool(name)
    console.print("[green]Removed.[/green]")


# -- Device commands ------------------------------------------------------------


@devices.command("list")
@with_light
def devices_list(light: Light):
    """List information for all devices registered on this account."""
    all_devices = light.devices.list_devices()

    def render_human_readable():
        table = Table(show_header=True)
        table.add_column("Device ID")
        table.add_column("Phone Number")
        table.add_column("Serial Number")
        table.add_column("SKU")

        for d in all_devices:
            table.add_row(
                d.id, d.phone_number or "[dim]unknown[/dim]", d.serial_number, d.sku
            )

        console.print(table)

    render(all_devices, render_human_readable)


# -- Schema ---------------------------------------------------------------------


@cli.command()
@click.option(
    "--hash",
    "hash_only",
    is_flag=True,
    help="Show only the schema's SHA-256 hash.",
)
def schema(hash_only):
    """Generate JSON Schema for every `--json`-enabled command's output."""
    from light_cli_tui.schema import generate_schema, schema_hash

    if hash_only:
        h = schema_hash()
        render({"hash": h}, lambda: click.echo(h))
        return

    doc = generate_schema()
    render(doc, lambda: console.print_json(json.dumps(doc)))


# -- Auth -----------------------------------------------------------------------


@cli.command()
@click.pass_context
def logout(ctx):
    """Clear the cached session.

    Forces a fresh login and device lookup on the next command. Does not
    require valid credentials or network access to run.
    """
    obj = ctx.obj or {}
    light = Light(
        email=obj.get("email"),
        email_file=obj.get("email_file"),
        password=obj.get("password"),
        password_file=obj.get("password_file"),
        phone=obj.get("phone_number"),
        phone_file=obj.get("phone_number_file"),
        device_id=obj.get("device_id"),
        device_id_file=obj.get("device_id_file"),
    )
    light.clear_cache()
    console.print("[green]Logged out.[/green]")


# -- TUI ------------------------------------------------------------------------


@cli.command()
@click.pass_context
def tui(ctx):
    """Launch the interactive terminal UI.

    A full-screen interface for browsing and managing your music library
    with vim-style keybindings.
    """
    try:
        from light_cli_tui.tui import LightConfig, run_tui
    except ImportError:
        raise click.UsageError(
            "The TUI requires extra dependencies. Install with: "
            "pip install 'light-phone-cli-tui[tui]'"
        )

    obj = ctx.obj or {}
    run_tui(
        LightConfig(
            email=obj.get("email"),
            email_file=obj.get("email_file"),
            password=obj.get("password"),
            password_file=obj.get("password_file"),
            phone=obj.get("phone_number"),
            phone_file=obj.get("phone_number_file"),
            device_id=obj.get("device_id"),
            device_id_file=obj.get("device_id_file"),
        )
    )


if __name__ == "__main__":
    cli()
