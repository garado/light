"""Interactive fuzzy-pick and confirm helpers."""

import click

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from rich.console import Console
from typing import Callable, Hashable, Iterable, TypeVar

from light_cli_tui.fuzzy import fuzzy_filter
from light_cli_tui.output import is_json_mode

T = TypeVar("T")

MAX_FUZZY_CANDIDATES = 30


def fuzzy_pick_interactive(
    queries: Iterable[str],
    items: Iterable[T],
    fields: Callable[[T], tuple[str, ...]],
    label: Callable[[T], str],
    id_key: Callable[[T], Hashable],
    console: Console,
) -> dict[Hashable, T] | None:
    """Prompt the user to pick items matching each query via a checkbox list.

    Returns:
        Selected items keyed by `id_key`, or None if the user aborted a picker.
    """
    items = list(items)
    selected: dict[Hashable, T] = {}

    for query in queries:
        scored = fuzzy_filter(query, items, key=fields)

        if not scored:
            console.print(f"[yellow]No matches for {query!r}.[/yellow]")
            continue

        truncated = len(scored) > MAX_FUZZY_CANDIDATES
        candidates = scored[:MAX_FUZZY_CANDIDATES]
        if truncated:
            console.print(
                f"[dim]{len(scored)} items matched {query!r}; "
                f"showing top {MAX_FUZZY_CANDIDATES}. Narrow your search to see more.[/dim]"
            )

        lookup = {id_key(t): t for _, t in candidates}

        picked_ids = inquirer.checkbox(
            message=f"Select items matching {query!r}:",
            choices=[Choice(value=id_key(t), name=label(t)) for _, t in candidates],
            raise_keyboard_interrupt=False,
            mandatory=False,
            long_instruction="(space to select, enter to confirm, ctrl-c to cancel)",
        ).execute()

        if picked_ids is None:
            return None

        for pid in picked_ids:
            selected[pid] = lookup[pid]

    return selected


def pick_interactive(
    items: Iterable[T],
    label: Callable[[T], str],
    id_key: Callable[[T], Hashable],
    console: Console,
    message: str = "Select items:",
) -> dict[Hashable, T] | None:
    """Prompt the user to pick from a fixed, already-filtered list via a checkbox list.

    Returns:
        Selected items keyed by `id_key`, or None if the user aborted.
    """
    items = list(items)
    truncated = len(items) > MAX_FUZZY_CANDIDATES
    candidates = items[:MAX_FUZZY_CANDIDATES]
    if truncated:
        console.print(
            f"[dim]{len(items)} tracks matched; showing top {MAX_FUZZY_CANDIDATES}. "
            "Narrow your search to see more.[/dim]"
        )

    lookup = {id_key(t): t for t in candidates}

    picked_ids = inquirer.checkbox(
        message=message,
        choices=[Choice(value=id_key(t), name=label(t), enabled=True) for t in candidates],
        raise_keyboard_interrupt=False,
        mandatory=False,
        long_instruction="(space to toggle, enter to confirm, ctrl-c to cancel)",
    ).execute()

    if picked_ids is None:
        return None

    return {pid: lookup[pid] for pid in picked_ids}


def prompt_track_edit(label: str, title: str, artist: str, album: str) -> tuple[str, str, str] | None:
    """Prompt for a track's new title/artist/album, prefilled with its current values.

    Returns:
        (title, artist, album) with the edited values, or None if the user cancelled.
    """
    click.echo(f"Editing: {label}")

    new_title = inquirer.text(
        message="Title:", default=title, raise_keyboard_interrupt=False, mandatory=False
    ).execute()
    if new_title is None:
        return None

    new_artist = inquirer.text(
        message="Artist:", default=artist, raise_keyboard_interrupt=False, mandatory=False
    ).execute()
    if new_artist is None:
        return None

    new_album = inquirer.text(
        message="Album:", default=album, raise_keyboard_interrupt=False, mandatory=False
    ).execute()
    if new_album is None:
        return None

    return new_title, new_artist, new_album


def prompt_batch_edit() -> tuple[str | None, str | None, str | None] | None:
    """Prompt for new title/artist/album to apply to multiple tracks at once.

    Fields are left blank by default; a blank field means "leave unchanged" on
    every track, since tracks in a batch generally don't share the same values.

    Returns:
        (title, artist, album), each None if left blank, or None if cancelled.
    """
    click.echo("Batch editing: leave a field blank to leave it unchanged.")

    new_title = inquirer.text(
        message="Title:", default="", raise_keyboard_interrupt=False, mandatory=False
    ).execute()
    if new_title is None:
        return None

    new_artist = inquirer.text(
        message="Artist:", default="", raise_keyboard_interrupt=False, mandatory=False
    ).execute()
    if new_artist is None:
        return None

    new_album = inquirer.text(
        message="Album:", default="", raise_keyboard_interrupt=False, mandatory=False
    ).execute()
    if new_album is None:
        return None

    return (new_title or None, new_artist or None, new_album or None)


def fuzzy_pick_best(
    queries: Iterable[str],
    items: Iterable[T],
    fields: Callable[[T], tuple[str, ...]],
    id_key: Callable[[T], Hashable],
    console: Console,
) -> dict[Hashable, T]:
    """Auto-select every item tied for the top fuzzy score, for each query."""
    items = list(items)
    selected: dict[Hashable, T] = {}

    for query in queries:
        scored = fuzzy_filter(query, items, key=fields)
        if not scored:
            if not is_json_mode():
                console.print(f"[yellow]No matches for {query!r}.[/yellow]")
            continue
        top_score = scored[0][0]
        for score, t in scored:
            if score == top_score:
                selected[id_key(t)] = t

    return selected


def confirm_selection_with_repick(
    initial: dict[Hashable, T],
    label: Callable[[T], str],
    header: str,
    repick: Callable[[], dict[Hashable, T] | None],
    console: Console,
) -> list[T] | None:
    """Show a confirm loop: [Y]es proceeds, [n]o aborts, [p]ick re-invokes `repick`.

    Returns:
        The final list of selected items, or None if aborted/declined.
    """
    selected = initial
    while True:
        items = list(selected.values())
        console.print(f"{header} ({len(items)}):")
        for t in items:
            console.print(f"  {label(t)}")

        try:
            choice = click.prompt(
                "Proceed? [Y]es / [n]o / [p]ick matches by hand instead",
                default="y",
                show_default=False,
                type=click.Choice(["y", "n", "p"], case_sensitive=False),
            )
        except (click.Abort, KeyboardInterrupt):
            console.print("\n[yellow]Aborted.[/yellow]")
            return None
        if choice == "n":
            return None
        if choice == "y":
            return items

        repicked = repick()
        if repicked is None:
            console.print("[yellow]Aborted.[/yellow]")
            return None
        selected = repicked
