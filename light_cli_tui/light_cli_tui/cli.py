"""
█░░ █ █▀▀ █░█ ▀█▀   █▀▀ █░░ █   ▄█▄   ▀█▀ █░█ █
█▄▄ █ █▄█ █▀█ ░█░   █▄▄ █▄▄ █   ░▀░   ░█░ █▄█ █

Command line tools for Light devices.
"""

import json
import logging
import os
import re
from pathlib import Path

import rich_click as click
from rich.console import Console, HighlighterType
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
    pick_interactive,
    prompt_batch_edit,
    prompt_track_edit,
)
from light_cli_tui.output import render, render_error, resolve_destructive_action


click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.STYLE_COMMANDS_TABLE_COLUMN_WIDTH_RATIO = (1, 3)

console = Console()
log = logging.getLogger(f"light.{__name__}")

_HELP_DIR = Path(__file__).parent / "help"


def _help(name: str) -> str:
    """Load a command's --help body from help/<name>.md."""
    return (_HELP_DIR / f"{name}.md").read_text()


def destructive_options(dry_run_help: str):
    """Bundle the shared --yes/--dry-run options for a destructive command."""

    def decorator(f):
        f = click.option("--dry-run", is_flag=True, default=False, help=dry_run_help)(f)
        f = click.option(
            "--yes", "-y", is_flag=True, default=False, help="Skip confirmation prompt."
        )(f)
        return f

    return decorator


class JsonAwareGroup(click.RichGroup):
    """Wrapper for command execution adding JSON output support for failures."""

    def parse_args(self, ctx: click.Context, args: list[str]) -> list[str]:
        """Let this group's boolean flags (e.g. --json) appear anywhere on the
        command line, not just before the subcommand name.

        This means you can do e.g. `light music list --json` instead of being restricted
        to `light --json music list`.
        """
        flag_opts = {
            opt
            for param in self.params
            if isinstance(param, click.Option) and param.is_flag
            for opt in param.opts
        }
        flags = [a for a in args if a in flag_opts]
        rest = [a for a in args if a not in flag_opts]
        return super().parse_args(ctx, flags + rest)

    def invoke(self, ctx: click.Context):
        try:
            return super().invoke(ctx)
        except click.ClickException as e:
            if (ctx.obj or {}).get("json"):
                render_error(e.format_message())
                ctx.exit(e.exit_code)
            raise


@click.group(
    cls=JsonAwareGroup,
    context_settings={"help_option_names": ["-h", "--help"]},
    help=_help("cli"),
)
@click.version_option(
    None, "-v", "--version", package_name="light-phone-cli-tui", prog_name="light"
)
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


@cli.group(help=_help("music"))
def music():
    pass


@cli.group(help=_help("podcasts"))
def podcasts():
    pass


@cli.group(help=_help("notes"))
def notes():
    pass


@cli.group(help=_help("devices"))
def devices():
    pass


# -- Podcast commands ----------------------------------------------------------


@podcasts.command("add", help=_help("podcasts_add"))
@with_light
@click.argument("rss_feed_url")
def podcasts_add(light: Light, rss_feed_url):
    p = light.podcast.add_podcast(rss_feed_url)

    def render_human_readable():
        console.print(f"[green]Added:[/green] {p.title or rss_feed_url}")
        if p.publisher:
            console.print(f"[dim]Publisher:[/dim] {p.publisher}")

    render(p, render_human_readable)


@podcasts.command("list", help=_help("podcasts_list"))
@with_light
def podcasts_list(light: Light):
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


@podcasts.command("delete", help=_help("podcasts_delete"))
@with_light
@click.argument("title", required=False)
@click.option(
    "--id",
    "ids",
    default=None,
    help="Unfollow by exact followed_podcast_id; comma-separated for bulk deletes.",
)
@destructive_options("Show which podcasts would be unfollowed, without unfollowing them.")
def podcasts_delete(light: Light, title, ids, yes, dry_run):
    if title and ids:
        raise click.UsageError("Provide either TITLE or --id, not both.")
    if not title and not ids:
        raise click.UsageError("Provide TITLE or --id.")

    podcasts = light.podcast.get_podcasts()

    if ids:
        id_list = [i.strip() for i in ids.split(",")]
        if any(not i for i in id_list):
            raise click.UsageError(f"Could not parse --id value: {ids!r}")
        by_id = {p.followed_podcast_id: p for p in podcasts}
        missing = [i for i in id_list if i not in by_id]
        if missing:
            raise click.UsageError(f"No podcast(s) found with id: {', '.join(missing)}")
        matches = [by_id[i] for i in id_list]
    else:
        matches = [p for p in podcasts if p.title == title]

    def render_human_readable():
        if not matches:
            console.print(f"[yellow]No podcast found with title: {title}[/yellow]")
            return
        for p in matches:
            console.print(f"  {p.title}")

    if not matches:
        render(matches, render_human_readable)
        return

    proceed = resolve_destructive_action(
        matches,
        render_human_readable,
        yes=yes,
        dry_run=dry_run,
        preview_header="This will unfollow the following podcast(s):",
        confirm_message="Unfollow?",
    )
    if not proceed:
        return

    for p in matches:
        light.podcast.delete_podcast_by_id(p.followed_podcast_id)
    render(matches, render_human_readable)


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


@music.command("upload", help=_help("music_upload"))
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


@music.command("delete-all", help=_help("music_delete_all"))
@with_light
def music_delete_all(light: Light):
    if not click.confirm("This will delete ALL tracks on the device. Proceed?"):
        return

    if input('Type "yes i am sure" to confirm: ') != "yes i am sure":
        return

    light.music.delete_all_tracks()


@music.command("delete", help=_help("music_delete"))
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


@music.command("sort", help=_help("music_sort"))
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


@music.command("update", help=_help("music_update"))
@with_light
@click.argument("songs", nargs=-1)
@click.option(
    "--title", "-t", "title_regex", help="Select tracks whose title matches this regex pattern."
)
@click.option(
    "--artist", "-a", "artist_regex", help="Select tracks whose artist matches this regex pattern."
)
@click.option(
    "--album", "-b", "album_regex", help="Select tracks whose album matches this regex pattern."
)
@click.option(
    "--id",
    "ids",
    default=None,
    help="Select track(s) by ID (comma-separated for bulk edits)."
)
@click.option("--new-title", default=None, help="New track title.")
@click.option("--new-artist", default=None, help="New artist name.")
@click.option("--new-album", default=None, help="New album name.")
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    default=False,
    help="Skip the picker and batch/individual prompt. Requires --new-title/"
    "--new-artist/--new-album.",
)
def music_update(
    light: Light,
    songs,
    title_regex,
    artist_regex,
    album_regex,
    ids,
    new_title,
    new_artist,
    new_album,
    yes,
):
    songs = tuple(s for s in songs if s.strip())
    regex_given = title_regex or artist_regex or album_regex

    if ids:
        id_list = [i.strip() for i in ids.split(",")]
        if any(not i for i in id_list):
            raise click.UsageError(f"Could not parse --id value: {ids!r}")
        ids = tuple(id_list)
    else:
        ids = ()

    modes_given = sum([bool(songs), bool(regex_given), bool(ids)])
    if modes_given > 1:
        raise click.UsageError(
            "Provide song titles, --title/--artist/--album, or --id — not more than one."
        )
    if modes_given == 0:
        raise click.UsageError(
            "Provide song titles, --id, or one of --title/--artist/--album."
        )

    flags_given = new_title or new_artist or new_album
    if yes and not flags_given:
        raise click.UsageError(
            "--yes requires at least one of --new-title/--new-artist/--new-album."
        )

    tracks = light.music.get_tracks()

    def pick_from(candidates):
        if yes or flags_given:
            return candidates
        selected = pick_interactive(
            candidates,
            label=lambda t: f"{t.artist} — {t.album} — {t.title}",
            id_key=lambda t: t.audio_id,
            console=console,
            message="Select tracks to edit:",
        )
        return None if selected is None else list(selected.values())

    if ids:
        by_id = {t.audio_id: t for t in tracks}
        missing = [i for i in ids if i not in by_id]
        if missing:
            raise click.UsageError(f"No track(s) found with id: {', '.join(missing)}")
        to_update = pick_from([by_id[i] for i in ids])
    elif regex_given:
        candidates = _filter_tracks_by_regex(tracks, title_regex, artist_regex, album_regex)
        if not candidates:
            console.print("[yellow]No matching tracks.[/yellow]")
            return
        to_update = pick_from(candidates)
    else:
        if yes or flags_given:
            selected = fuzzy_pick_best(
                songs,
                tracks,
                fields=lambda t: (t.title, t.artist, t.album),
                id_key=lambda t: t.audio_id,
                console=console,
            )
            to_update = list(selected.values())
        else:
            selected = fuzzy_pick_interactive(
                songs,
                tracks,
                fields=lambda t: (t.title, t.artist, t.album),
                label=lambda t: f"{t.artist} — {t.album} — {t.title}",
                id_key=lambda t: t.audio_id,
                console=console,
            )
            to_update = None if selected is None else list(selected.values())

    if to_update is None:
        console.print("[yellow]Aborted.[/yellow]")
        return
    if not to_update:
        console.print("[yellow]No matching tracks.[/yellow]")
        return

    if flags_given:
        batch_values = (new_title, new_artist, new_album)
        if not yes:
            console.print(f"[bold]This will update {len(to_update)} track(s):[/bold]")
            for track in to_update:
                console.print(f"  [dim]{track.artist} — {track.album} — {track.title}[/dim]")

            changes = []
            if new_title:
                changes.append(f"Title -> [green]{new_title}[/green]")
            if new_artist:
                changes.append(f"Artist -> [green]{new_artist}[/green]")
            if new_album:
                changes.append(f"Album -> [green]{new_album}[/green]")
            console.print("  " + ", ".join(changes))

            if not click.confirm("Proceed?"):
                console.print("[yellow]Aborted.[/yellow]")
                return
    elif len(to_update) > 1:
        choice = click.prompt(
            f"{len(to_update)} tracks selected. [b]atch edit (same values for all) "
            "/ [i]ndividually edit each?",
            default="i",
            show_default=False,
            type=click.Choice(["b", "i"], case_sensitive=False),
        )
        if choice == "b":
            batch_values = prompt_batch_edit()
            if batch_values is None:
                console.print("[yellow]Aborted.[/yellow]")
                return
            if all(v is None for v in batch_values):
                console.print("[yellow]No fields set, nothing to update.[/yellow]")
                return
        else:
            batch_values = None
    else:
        batch_values = None

    for track in to_update:
        if batch_values is not None:
            title, artist, album = batch_values
        else:
            edited = prompt_track_edit(
                label=f"{track.artist} — {track.album} — {track.title}",
                title=track.title,
                artist=track.artist,
                album=track.album,
            )
            if edited is None:
                console.print("[yellow]Skipped.[/yellow]")
                continue
            title, artist, album = edited
            if (title, artist, album) == (track.title, track.artist, track.album):
                console.print(f"[yellow]No changes:[/yellow] {track.artist} — {track.title}")
                continue

        light.music.update_track_metadata(track.audio_id, title=title, artist=artist, album=album)
        console.print(f"[green]Updated:[/green] {track.artist} — {track.title}")


@music.command("list", help=_help("music_list"))
@with_light
@click.option(
    "--title", "-t", "title_regex", help="Only show tracks whose title matches this regex pattern."
)
@click.option(
    "--artist", "-a", "artist_regex", help="Only show tracks whose artist matches this regex pattern."
)
@click.option(
    "--album", "-b", "album_regex", help="Only show tracks whose album matches this regex pattern."
)
@click.option(
    "--show-id",
    "-i",
    "show_id",
    is_flag=True,
    default=False,
    help="Include audio ID in output.",
)
@click.option(
    "--show-filename",
    "-f",
    "show_filename",
    is_flag=True,
    default=False,
    help="Include original uploaded filename in output.",
)
def music_list(
    light: Light,
    title_regex: str | None,
    artist_regex: str | None,
    album_regex: str | None,
    show_id: bool,
    show_filename: bool,
):
    tracks = light.music.get_tracks()
    tracks = _filter_tracks_by_regex(tracks, title_regex, artist_regex, album_regex)

    def render_human_readable():
        table = Table(show_header=True)
        table.add_column("#", style="dim", width=4)
        table.add_column("Title")
        table.add_column("Artist")
        table.add_column("Album")
        if show_id:
            table.add_column("ID")
        if show_filename:
            table.add_column("Filename")

        for i, track in enumerate(tracks, 1):
            row = [str(i)]
            row.extend([track.title, track.artist, track.album])
            if show_id:
                row.append(track.audio_id)
            if show_filename:
                row.append(track.filename)
            table.add_row(*row)

        console.print(table)

    render(tracks, render_human_readable)


# -- Notes commands -------------------------------------------------------------


@notes.command("list", help=_help("notes_list"))
@with_light
@click.option(
    "--id",
    "-i",
    "show_id",
    default=False,
    type=bool,
    is_flag=True,
    help="Include note ID in output.",
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
    all_notes = light.notes.get_notes()

    def _build_table(progress_cb=None) -> Table:
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
                    content = light.notes.get_note_content(note).decode(errors="replace")
                    if content and content.strip():
                        preview = content.splitlines()[0]
                    else:
                        preview = "[dim](empty)[/dim]"
                row.append(preview)

            table.add_row(*row)
            if progress_cb:
                progress_cb(i)

        return table

    def render_human_readable():
        if content_preview and all_notes:
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console,
            ) as progress:
                task_id = progress.add_task(
                    "Fetching content previews...", total=len(all_notes)
                )
                table = _build_table(lambda i: progress.update(task_id, completed=i))
        else:
            table = _build_table()

        console.print(table)

    render(all_notes, render_human_readable)


@notes.command("download", help=_help("notes_download"))
@with_light
@click.argument("path")
def notes_download(light: Light, path: str):
    light.notes.download_notes(path)


@notes.command("add", help=_help("notes_add"))
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
    if content is None and content_file is None:
        raise click.UsageError("Provide CONTENT or --file.")

    if content is not None and content_file is not None:
        raise click.UsageError("CONTENT and --file are mutually exclusive.")

    if content_file:
        light.notes.create_text_note(title, content_file, content_is_path=True)
    else:
        light.notes.create_text_note(title, content)


# -- Tools commands ------------------------------------------------------------


@cli.group(help=_help("tools"))
def tools():
    pass


@tools.command("list", help=_help("tools_list"))
@with_light
def tools_list(light: Light):
    all_tools = light.tools.get_tools()

    def render_human_readable():
        table = Table(show_header=True)
        table.add_column("Title")

        for t in all_tools:
            table.add_row(t.title)

        console.print(table)

    render(all_tools, render_human_readable)


@tools.command("add", help=_help("tools_add"))
@with_light
@click.argument(
    "name", type=click.Choice([t.value for t in ToolName], case_sensitive=False)
)
def tools_add(light: Light, name: str):
    tool = light.tools.add_tool(name)
    console.print(f"[green]Installed:[/green] {tool.title}")


@tools.command("remove", help=_help("tools_remove"))
@with_light
@click.argument(
    "name", type=click.Choice([t.value for t in ToolName], case_sensitive=False)
)
def tools_remove(light: Light, name: str):
    if not click.confirm(f"Remove {name}?"):
        return
    light.tools.remove_tool(name)
    console.print("[green]Removed.[/green]")


# -- Device commands ------------------------------------------------------------


@devices.command("list", help=_help("devices_list"))
@with_light
def devices_list(light: Light):
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


@cli.command(help=_help("schema"))
@click.option(
    "--hash",
    "hash_only",
    is_flag=True,
    help="Show only the schema's SHA-256 hash.",
)
def schema(hash_only):
    from light_cli_tui.schema import generate_schema, schema_hash

    if hash_only:
        h = schema_hash()
        render({"hash": h}, lambda: click.echo(h))
        return

    doc = generate_schema()
    render(doc, lambda: console.print_json(json.dumps(doc)))


# -- Auth -----------------------------------------------------------------------


@cli.command(help=_help("logout"))
@click.pass_context
def logout(ctx):
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


@cli.command(help=_help("tui"))
@click.pass_context
def tui(ctx):
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
