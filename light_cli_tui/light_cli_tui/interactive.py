"""Interactive fuzzy-pick and confirm helpers."""

import click

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from rich.console import Console
from typing import Callable, Hashable, Iterable, TypeVar

from light_cli_tui.fuzzy import fuzzy_filter

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
