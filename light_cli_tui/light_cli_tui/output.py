"""JSON output helpers for --json mode.

Every command's JSON output is wrapped as `{"data": <value>, "error": <string or null>}`.
"""

import click
import dataclasses
import json

from typing import Any, Callable


def resolve_destructive_action(
    data: Any,
    render_human_readable: Callable[[], None],
    *,
    yes: bool,
    dry_run: bool,
    confirm_message: str,
) -> bool:
    """Handle the shared --json/--yes/--dry-run/confirm flow for destructive commands.

    On `--dry-run`, renders `data` as the preview and tells the caller not to proceed.
    Otherwise, resolves confirmation (skipped via `--yes`, or via an interactive prompt)
    and tells the caller whether to proceed with the action. `--json` requires `--yes`
    or `--dry-run` since an interactive prompt can't be answered by a JSON consumer.

    Returns:
        True if the caller should proceed with the action, False otherwise.
    """
    if yes and dry_run:
        raise click.UsageError("--yes and --dry-run are mutually exclusive.")

    if dry_run:
        render(data, render_human_readable)
        return False

    if not yes:
        if is_json_mode():
            raise click.UsageError(
                "--json requires --yes or --dry-run for destructive commands."
            )
        render_human_readable()
        if not click.confirm(confirm_message):
            return False

    return True


def render(data: Any, human: Callable[[], None]) -> None:
    """Render data in either JSON or human-readable format based on if CLI `--json` flag was set.

    Args:
        data: The data to be rendered.
        human: Alternate function to render data in human-readable format.
    """
    if is_json_mode():
        _render_json(data)
    else:
        human()


def render_error(message: str) -> None:
    """Render an error in `--json` mode."""
    click.echo(json.dumps({"data": None, "error": message}, indent=2))


def is_json_mode() -> bool:
    ctx = click.get_current_context()
    obj = ctx.find_root().obj or {}
    return bool(obj.get("json"))


def _render_json(data: Any) -> None:
    """Output JSON data to stdout.

    `data` renders as `{"data": ..., "error": null}`.
    """
    click.echo(json.dumps({"data": _to_jsonable(data), "error": None}, indent=2))


def _to_jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return dataclasses.asdict(value)
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(v) for v in value]
    return value
